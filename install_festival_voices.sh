#!/bin/bash

sudo apt-get install -y festival festlex-cmu festlex-poslex festlex-oald libestools1.2 unzip
sudo apt-get install -y festvox-don festvox-rablpc16k festvox-kallpc16k festvox-kdlpc16k

mkdir /tmp/cmu_tmp
mv festvox_cmu_us_fem_cg.tar.gz /tmp/cmu_tmp
pushd .
cd /tmp/cmu_tmp/

#wget -c http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_awb_arctic-0.90-release.tar.bz2
#wget -c http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_bdl_arctic-0.95-release.tar.bz2
#wget -c http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_jmk_arctic-0.95-release.tar.bz2
#wget -c http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_clb_arctic-0.95-release.tar.bz2
#wget -c http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_rms_arctic-0.95-release.tar.bz2
#wget -c http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_slt_arctic-0.95-release.tar.bz2


for t in `ls festvox_cmu_*` ;
do
    tar xf $t ;
done
sudo mkdir -p /usr/share/festival/voices/us/
#sudo cp -pr $(ls | grep -v .bz2) /usr/share/festival/voices/us/
sudo mv festival/lib/voices/* /usr/share/festival/voices/us/

#for d in `ls /usr/share/festival/voices/english` ; do
#if [[ "$d" =~ "cmu_us_" ]] ; then
#    sudo mv "/usr/share/festival/voices/us/${d}" "/usr/share/festival/voices/us/${d}_clunits" 
#fi ; done

popd
