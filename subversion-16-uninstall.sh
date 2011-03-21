#!/bin/bash
# -*- coding:utf-8 -*-

# subversion-16-upgrade.sh でインストールしたSubversionをアンインストールする.


export KANON_HOME=/opt/kanon

function not_supported {
    echo "サポートされていないOSです。"
    echo "現在サポートされいているOSは、"
    echo ""
    echo "  * CentOS 5.x (Experimental)"
    echo ""
    echo "です。"
    exit 1
}

function check_os {
    if [ ! -f /etc/redhat-release ]
    then
        not_supported
    else
        CHK=`egrep "CentOS release 5|Red Hat Enterprise Linux .* 5" /etc/redhat-release`
        if [ "$CHK" == '' ]
        then
            not_supported
        fi
    fi
}

check_os


# Apache Modules.
rm -f /usr/lib/httpd/modules/mod_authz_svn.so
rm -f /usr/lib/httpd/modules/mod_dav_svn.so
rm -f /usr/lib64/httpd/modules/mod_authz_svn.so
rm -f /usr/lib64/httpd/modules/mod_dav_svn.so

# Subversion Commands.
rm -f /opt/kanon/bin/neon-config
rm -f /opt/kanon/bin/svn
rm -f /opt/kanon/bin/svnadmin
rm -f /opt/kanon/bin/svndumpfilter
rm -f /opt/kanon/bin/svnlook
rm -f /opt/kanon/bin/svnserve
rm -f /opt/kanon/bin/svnsync
rm -f /opt/kanon/bin/svnversion

# include headers.
rm -rf /opt/kanon/include/neon
rm -rf /opt/kanon/include/serf-0
rm -rf /opt/kanon/include/subversion-1

# python bindings for subversion.
rm -rf /opt/kanon/lib/svn-python
rm -f /opt/kanon/lib/python2.6/site-packages/libsvn
rm -f /opt/kanon/lib/python2.6/site-packages/svn

# libs.
rm -rf /opt/kanon/lib/libneon*
rm -rf /opt/kanon/lib/libserf-0.*
rm -rf /opt/kanon/lib/libsvn_*

# package config.
rm -f /opt/kanon/lib/pkgconfig/neon.pc

# man
rm -f /opt/kanon/man/man1/svn.1
rm -f /opt/kanon/man/man1/svnadmin.1
rm -f /opt/kanon/man/man1/svndumpfilter.1
rm -f /opt/kanon/man/man1/svnlook.1
rm -f /opt/kanon/man/man1/svnsync.1
rm -f /opt/kanon/man/man1/svnversion.1
rm -f /opt/kanon/man/man5/svnserve.conf.5
rm -f /opt/kanon/man/man8/svnserve.8

# share doc.
rm -rf /opt/kanon/share/doc/neon-0.28.6

# share locale.
rm -f /opt/kanon/share/locale/cs/LC_MESSAGES/neon.mo
rm -f /opt/kanon/share/locale/de/LC_MESSAGES/neon.mo
rm -f /opt/kanon/share/locale/de/LC_MESSAGES/subversion.mo
rm -f /opt/kanon/share/locale/es/LC_MESSAGES/subversion.mo
rm -f /opt/kanon/share/locale/fr/LC_MESSAGES/neon.mo
rm -f /opt/kanon/share/locale/fr/LC_MESSAGES/subversion.mo
rm -f /opt/kanon/share/locale/it/LC_MESSAGES/subversion.mo
rm -f /opt/kanon/share/locale/ja/LC_MESSAGES/neon.mo
rm -f /opt/kanon/share/locale/ja/LC_MESSAGES/subversion.mo
rm -f /opt/kanon/share/locale/ko/LC_MESSAGES/subversion.mo
rm -f /opt/kanon/share/locale/nb/LC_MESSAGES/subversion.mo
rm -f /opt/kanon/share/locale/nn/LC_MESSAGES/neon.mo
rm -f /opt/kanon/share/locale/pl/LC_MESSAGES/neon.mo
rm -f /opt/kanon/share/locale/pl/LC_MESSAGES/subversion.mo
rm -f /opt/kanon/share/locale/pt_BR/LC_MESSAGES/subversion.mo
rm -f /opt/kanon/share/locale/ru/LC_MESSAGES/neon.mo
rm -f /opt/kanon/share/locale/sv/LC_MESSAGES/subversion.mo
rm -f /opt/kanon/share/locale/tr/LC_MESSAGES/neon.mo
rm -f /opt/kanon/share/locale/zh_CN/LC_MESSAGES/neon.mo
rm -f /opt/kanon/share/locale/zh_CN/LC_MESSAGES/subversion.mo
rm -f /opt/kanon/share/locale/zh_TW/LC_MESSAGES/subversion.mo

# share man.
rm -f /opt/kanon/share/man/man1/neon-config.1
rm -f /opt/kanon/share/man/man3/ne_add_request_header.3
rm -f /opt/kanon/share/man/man3/ne_addr_destroy.3
rm -f /opt/kanon/share/man/man3/ne_addr_error.3
rm -f /opt/kanon/share/man/man3/ne_addr_first.3
rm -f /opt/kanon/share/man/man3/ne_addr_next.3
rm -f /opt/kanon/share/man/man3/ne_addr_resolve.3
rm -f /opt/kanon/share/man/man3/ne_addr_result.3
rm -f /opt/kanon/share/man/man3/ne_buffer.3
rm -f /opt/kanon/share/man/man3/ne_buffer_altered.3
rm -f /opt/kanon/share/man/man3/ne_buffer_append.3
rm -f /opt/kanon/share/man/man3/ne_buffer_clear.3
rm -f /opt/kanon/share/man/man3/ne_buffer_concat.3
rm -f /opt/kanon/share/man/man3/ne_buffer_create.3
rm -f /opt/kanon/share/man/man3/ne_buffer_destroy.3
rm -f /opt/kanon/share/man/man3/ne_buffer_finish.3
rm -f /opt/kanon/share/man/man3/ne_buffer_grow.3
rm -f /opt/kanon/share/man/man3/ne_buffer_ncreate.3
rm -f /opt/kanon/share/man/man3/ne_buffer_zappend.3
rm -f /opt/kanon/share/man/man3/ne_calloc.3
rm -f /opt/kanon/share/man/man3/ne_close_connection.3
rm -f /opt/kanon/share/man/man3/ne_forget_auth.3
rm -f /opt/kanon/share/man/man3/ne_get_error.3
rm -f /opt/kanon/share/man/man3/ne_get_request_flag.3
rm -f /opt/kanon/share/man/man3/ne_get_response_header.3
rm -f /opt/kanon/share/man/man3/ne_get_scheme.3
rm -f /opt/kanon/share/man/man3/ne_get_server_hostport.3
rm -f /opt/kanon/share/man/man3/ne_get_session_flag.3
rm -f /opt/kanon/share/man/man3/ne_get_status.3
rm -f /opt/kanon/share/man/man3/ne_has_support.3
rm -f /opt/kanon/share/man/man3/ne_i18n_init.3
rm -f /opt/kanon/share/man/man3/ne_iaddr_cmp.3
rm -f /opt/kanon/share/man/man3/ne_iaddr_free.3
rm -f /opt/kanon/share/man/man3/ne_iaddr_make.3
rm -f /opt/kanon/share/man/man3/ne_iaddr_print.3
rm -f /opt/kanon/share/man/man3/ne_iaddr_typeof.3
rm -f /opt/kanon/share/man/man3/ne_malloc.3
rm -f /opt/kanon/share/man/man3/ne_oom_callback.3
rm -f /opt/kanon/share/man/man3/ne_print_request_header.3
rm -f /opt/kanon/share/man/man3/ne_qtoken.3
rm -f /opt/kanon/share/man/man3/ne_realloc.3
rm -f /opt/kanon/share/man/man3/ne_request_create.3
rm -f /opt/kanon/share/man/man3/ne_request_destroy.3
rm -f /opt/kanon/share/man/man3/ne_request_dispatch.3
rm -f /opt/kanon/share/man/man3/ne_response_header_iterate.3
rm -f /opt/kanon/share/man/man3/ne_session_create.3
rm -f /opt/kanon/share/man/man3/ne_session_destroy.3
rm -f /opt/kanon/share/man/man3/ne_session_proxy.3
rm -f /opt/kanon/share/man/man3/ne_set_connect_timeout.3
rm -f /opt/kanon/share/man/man3/ne_set_error.3
rm -f /opt/kanon/share/man/man3/ne_set_proxy_auth.3
rm -f /opt/kanon/share/man/man3/ne_set_read_timeout.3
rm -f /opt/kanon/share/man/man3/ne_set_request_body_buffer.3
rm -f /opt/kanon/share/man/man3/ne_set_request_body_fd.3
rm -f /opt/kanon/share/man/man3/ne_set_request_body_fd64.3
rm -f /opt/kanon/share/man/man3/ne_set_request_flag.3
rm -f /opt/kanon/share/man/man3/ne_set_server_auth.3
rm -f /opt/kanon/share/man/man3/ne_set_session_flag.3
rm -f /opt/kanon/share/man/man3/ne_set_useragent.3
rm -f /opt/kanon/share/man/man3/ne_shave.3
rm -f /opt/kanon/share/man/man3/ne_sock_exit.3
rm -f /opt/kanon/share/man/man3/ne_sock_init.3
rm -f /opt/kanon/share/man/man3/ne_ssl_cert_cmp.3
rm -f /opt/kanon/share/man/man3/ne_ssl_cert_export.3
rm -f /opt/kanon/share/man/man3/ne_ssl_cert_free.3
rm -f /opt/kanon/share/man/man3/ne_ssl_cert_identity.3
rm -f /opt/kanon/share/man/man3/ne_ssl_cert_import.3
rm -f /opt/kanon/share/man/man3/ne_ssl_cert_issuer.3
rm -f /opt/kanon/share/man/man3/ne_ssl_cert_read.3
rm -f /opt/kanon/share/man/man3/ne_ssl_cert_signedby.3
rm -f /opt/kanon/share/man/man3/ne_ssl_cert_subject.3
rm -f /opt/kanon/share/man/man3/ne_ssl_cert_write.3
rm -f /opt/kanon/share/man/man3/ne_ssl_clicert_decrypt.3
rm -f /opt/kanon/share/man/man3/ne_ssl_clicert_encrypted.3
rm -f /opt/kanon/share/man/man3/ne_ssl_clicert_free.3
rm -f /opt/kanon/share/man/man3/ne_ssl_clicert_name.3
rm -f /opt/kanon/share/man/man3/ne_ssl_clicert_owner.3
rm -f /opt/kanon/share/man/man3/ne_ssl_clicert_read.3
rm -f /opt/kanon/share/man/man3/ne_ssl_dname_cmp.3
rm -f /opt/kanon/share/man/man3/ne_ssl_readable_dname.3
rm -f /opt/kanon/share/man/man3/ne_ssl_set_verify.3
rm -f /opt/kanon/share/man/man3/ne_ssl_trust_cert.3
rm -f /opt/kanon/share/man/man3/ne_ssl_trust_default_ca.3
rm -f /opt/kanon/share/man/man3/ne_status.3
rm -f /opt/kanon/share/man/man3/ne_strdup.3
rm -f /opt/kanon/share/man/man3/ne_strndup.3
rm -f /opt/kanon/share/man/man3/ne_token.3
rm -f /opt/kanon/share/man/man3/ne_version_match.3
rm -f /opt/kanon/share/man/man3/ne_version_string.3
rm -f /opt/kanon/share/man/man3/ne_xml_create.3
rm -f /opt/kanon/share/man/man3/ne_xml_destroy.3
rm -f /opt/kanon/share/man/man3/neon.3

