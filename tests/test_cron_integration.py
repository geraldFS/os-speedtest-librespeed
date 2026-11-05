#!/usr/bin/env python3
"""Run actual cron manager's policy and mutation flow using a mock OPNsense Cron model.
No real system configuration is touched. This is NOT an OPNsense integration test.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import json, subprocess, os
ROOT=Path(__file__).resolve().parents[1]
BOOT=r'''<?php
namespace OPNsense\Cron {
    class Node {
        public $v;
        public function __construct($x) { $this->v=$x; }
        public function __get($key) { return $this->v[$key] ?? ''; }
        public function __set($key,$val) { $this->v[$key]=(string)$val; }
        public function getAttributes() { return ['uuid' => $this->v['uuid'] ?? '']; }
    }
    class JobCollection {
        public $items=[];
        public function __construct($raw) {foreach($raw as $r) $this->items[]=new Node($r);}
        public function iterateItems() {return $this->items;}
        public function Add() { $v = new Node(['uuid'=>'mock-created-uuid']); $this->items[]=$v; return $v; }
        public function del($uuid) {
          foreach ($this->items as $i=>$n) if (($n->v['uuid'] ?? '')===$uuid) {
            array_splice($this->items,$i,1); return true;
          }
          return false;
        }
    }
    class Cron {
        public $jobs;
        public function __construct() {
          $raw = json_decode(file_get_contents(getenv('CRON_STATE')),true);
          $this->jobs=(object)['job'=>new JobCollection($raw)];
          $GLOBALS['TEST_CRON_MODEL']=$this;
        }
        public function performValidation() {return [];}
        public function serializeToConfig() {}
    }
}
namespace OPNsense\Core {
    class Config {
      public static function getInstance() {return new self();}
      public function lock() {}
      public function save($metadata=null) {
        $items=$GLOBALS['TEST_CRON_MODEL']->jobs->job->iterateItems();
        $values=[];foreach ($items as $item) $values[]=$item->v;
        file_put_contents(getenv('CRON_STATE'),json_encode($values));
      }
    }
}
'''
with TemporaryDirectory() as td:
    tmp=Path(td)
    source=(ROOT/'src/manage-cron.php').read_text()
    bootstrap=tmp/'bootstrap.php'
    bootstrap.write_text(BOOT)
    manager=tmp/'manage-cron.php'
    # Replace only the OPNsense bootstrap path for isolated model tests.
    manager.write_text(source.replace("require_once '/usr/local/opnsense/mvc/script/load_phalcon.php';",f"require_once '{bootstrap}';"))
    (tmp/'cron_policy.php').write_text((ROOT/'src/cron_policy.php').read_text())
    state=tmp/'cron.json'
    env={**os.environ,'CRON_STATE':str(state)}
    OWN={'uuid':'owned','command':'csvspeedtest run','description':'LibreSpeed Reporting [os-speedtest-csv-reporting]','parameters':'','minutes':'15','hours':'*'}
    OLD={'uuid':'old','command':'speedtest run','description':'Mein alter Speedtest','parameters':''}
    USER={'uuid':'user','command':'csvspeedtest run','description':'Speedtest Test','parameters':''}
    def run(init,action):
        state.write_text(json.dumps(init))
        p=subprocess.run(['php',str(manager),action],text=True,capture_output=True,env=env)
        assert p.returncode==0,(action,p.stdout,p.stderr)
        return json.loads(state.read_text()),p.stdout
    fresh,out=run([],'--ensure')
    assert len(fresh)==1 and fresh[0]['command']=='csvspeedtest run',fresh
    assert fresh[0]['minutes']=='0' and fresh[0]['hours']=='*',fresh
    assert fresh[0]['enabled']=='1',fresh
    assert fresh[0]['origin']=='cron',fresh
    assert 'angelegt' in out,out
    old,out=run([OLD],'--ensure')
    assert old==[OLD] and 'Keine weitere' in out,(old,out)
    own,out=run([OWN],'--ensure')
    assert own==[OWN] and 'existiert bereits' in out,(own,out)
    both,out=run([OLD,OWN,USER],'--remove-owned')
    assert both==[OLD,USER],both
    no_owned,out=run([OLD,USER],'--remove-owned')
    assert no_owned==[OLD,USER],no_owned
    status,out=run([OLD],'--status')
    assert status==[OLD] and 'existing-user-job' in out,(status,out)
print('OPNsense Cron model flow simulated: new, existing, idempotent, tagged removal OK')
