<?php
namespace OPNsense\Csvspeedtest;

class IndexController extends \OPNsense\Base\IndexController
{
    public function indexAction()
    {
        $this->view->pick('OPNsense/Csvspeedtest/index');
    }
}
