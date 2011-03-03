#!/bin/sh

rm -fr resource/trac-plugins/*/dist resource/trac-plugins/*/build resource/trac-plugins/*/*.egg-info
find . -name "*.mo"  -exec rm {} \;