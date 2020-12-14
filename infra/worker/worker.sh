#!/bin/bash
. ~/bin/activate
. ~/vars.sh
exec /home/erp/bin/rq worker py3
