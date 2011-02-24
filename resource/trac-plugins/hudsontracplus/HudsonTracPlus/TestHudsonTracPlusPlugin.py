# -*- coding: utf-8 -*-
"""
Test for HudsonTracPlusPlugin
"""
from HudsonTracPlusPlugin import HudsonTracPlusPlugin
from trac.test import EnvironmentStub
from trac.config import Option

class TestHudsonTracPlusPlugin:
    def test_default_opt_hudson_url(self):
        env = EnvironmentStub()
        htpp = HudsonTracPlusPlugin(env)
        assert 'http://localhost:8010/hudson/' == htpp.hudson_url

    def test_default_opt_nav_url(self):
        env = EnvironmentStub()
        htpp = HudsonTracPlusPlugin(env)
        assert '/hudson/' == htpp.nav_url

    def test_default_opt_jobs(self):
        env = EnvironmentStub()
        htpp = HudsonTracPlusPlugin(env)
        assert [] == htpp.jobs

    def test_default_opt_disp_tab(self):
        env = EnvironmentStub()
        htpp = HudsonTracPlusPlugin(env)
        assert False == htpp.disp_tab

    def test_default_opt_navi_label(self):
        env = EnvironmentStub()
        htpp = HudsonTracPlusPlugin(env)
        assert 'Hudson' == htpp.navi_label

    def test_default_opt_username(self):
        env = EnvironmentStub()
        htpp = HudsonTracPlusPlugin(env)
        assert '' == htpp.username

    def test_default_opt_password(self):
        env = EnvironmentStub()
        htpp = HudsonTracPlusPlugin(env)
        assert '' == htpp.password

    def test_get_build_comment(self):
        from HudsonTracPlusPlugin import get_build_comment
        build = {'result': 'SUCCESS', 'description': 'メッセージ'}
        assert u'メッセージ at TIME' == get_build_comment(build, 'TIME')

if __name__ == '__main__':
    thtpp = TestHudsonTracPlusPlugin()
    thtpp.test_default_opt_hudson_url()
    thtpp.test_default_opt_nav_url()
    thtpp.test_default_opt_jobs()
    thtpp.test_default_opt_disp_tab()
    thtpp.test_default_opt_navi_label()
    thtpp.test_default_opt_username()
    thtpp.test_default_opt_password()
