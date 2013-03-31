#!/usr/bin/env bash

shopt -s expand_aliases

export ATLAS_LOCAL_ROOT_BASE=/home/hep/share/app/atlas/ATLASLocalRootBase
alias setupATLAS='source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh'
setupATLAS --quiet

dq2script=${ATLAS_LOCAL_ROOT_BASE}/packageSetups/atlasLocalDQ2ClientSetup.sh
alias localSetupDQ2Client='source ${dq2script}'

opts="--skipConfirm --dq2ClientVersion ${dq2ClientVersionVal} --quiet"
localSetupDQ2Client $opts

echo 'submitted from: ' $PBS_O_WORKDIR 
cd $PBS_O_WORKDIR

voms-proxy-init -voms atlas -noregen -q -cert local_cert

