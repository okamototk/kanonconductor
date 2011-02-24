#!/bin/sh

rm -fr resource/plugins/*/dist resource/plugins/*/build resource/plugins/*/*.egg-info
find . -name "*.mo"  -exec rm {} \;