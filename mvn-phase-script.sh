#!/bin/bash
# Copyright 2018 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


set -e

echo "running script: [$0] for module [$1] at stage [$2]"

export SETTINGS_FILE=${SETTINGS_FILE:-$HOME/.m2/settings.xml}
MVN_PROJECT_MODULEID="$1"
MVN_PHASE="$2"


FQDN="${MVN_PROJECT_GROUPID}.${MVN_PROJECT_ARTIFACTID}"
if [ "$MVN_PROJECT_MODULEID" == "__" ]; then
  MVN_PROJECT_MODULEID=""
fi

if [ -z "$WORKSPACE" ]; then
    WORKSPACE=$(pwd)
fi


# mvn phase in life cycle
MVN_PHASE="$2"


echo "MVN_PROJECT_MODULEID is            [$MVN_PROJECT_MODULEID]"
echo "MVN_PHASE is                       [$MVN_PHASE]"
echo "MVN_PROJECT_GROUPID is             [$MVN_PROJECT_GROUPID]"
echo "MVN_PROJECT_ARTIFACTID is          [$MVN_PROJECT_ARTIFACTID]"
echo "MVN_PROJECT_VERSION is             [$MVN_PROJECT_VERSION]"

run_tox_test()
{
  set -x
  CURDIR=$(pwd)
  if [[ ${CURDIR} =~ "-sonar" ]]
  then
    echo "====Sonar job, need execute tox."
    TOXINIS=$(find . -name "tox.ini")
    for TOXINI in "${TOXINIS[@]}"; do
      DIR=$(echo "$TOXINI" | rev | cut -f2- -d'/' | rev)
      cd "${CURDIR}/${DIR}"
      rm -rf ./venv-tox ./.tox
      virtualenv ./venv-tox
      source ./venv-tox/bin/activate
      pip install --upgrade pip
      pip install --upgrade tox argparse
      pip freeze
      tox
      deactivate
      rm -rf ./venv-tox ./.tox
    done
  else
    echo "====Not a sonar job, need not execute tox."
  fi
}


case $MVN_PHASE in
clean)
  echo "==> clean phase script"
  rm -rf ./venv-*
  ;;
test)
  echo "==> test phase script"
  run_tox_test
  ;;
*)
  echo "==> unprocessed phase"
  ;;
esac

