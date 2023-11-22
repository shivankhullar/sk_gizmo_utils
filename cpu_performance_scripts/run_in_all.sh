i=$PWD 
#for d in ./* ; do
    #echo "$d"
    #rm -rf $d/gizmo_imf_sk
    #echo "Removed old directory"
    #python clone_gizmo.py --repo_name=gizmo_imf_sk --dest_dir=$d
    #cd $d/gizmo_imf_sk
    #git reset --hard bc0ed35
    #cd $i
    #python gizmo_setup.py --repo_dir=$d/gizmo_imf_sk/
    #mkdir $d/output
    #touch $d/output/cpu.txt
    #cp ./*.py $d/gizmo_imf_sk/
    #cp ./*.hdf5 $d/gizmo_imf_sk/
    #cp ./*.sh $d/gizmo_imf_sk/
    #cp ./*.txt $d/gizmo_imf_sk/
#done

for x in {32,64,128,256,512} ; do
    s=46
    b=1e-1
    #cp ./params_M1e4_R10_S0_T1_B0.1_Res"$s"_n2_sol0.5_42.txt MHD_"$b"_core"$x"/gizmo_imf_sk/
    #cp ./M1e4_R10_S0_T1_B0.1_Res"$s"_n2_sol0.5_42.hdf5 MHD_"$b"_core"$x"/gizmo_imf_sk/
    #cp ./job_submit.sh MHD_"$b"_core"$x"/gizmo_imf_sk/
    #cp ./Config.sh MHD_"$b"_core"$x"/gizmo_imf_sk/
    #cp ./track_job.py MHD_"$b"_core"$x"/gizmo_imf_sk/
    echo MHD_"$b"_core"$x"
    ls -lh ./MHD_"$b"_core"$x"/output/
done

for x in {32,64,128,256,512} ; do
    s=100
    b=1e-2	
    #cp ./params_M1e4_R10_S0_T1_B0.1_Res"$s"_n2_sol0.5_42.txt MHD_"$b"_core"$x"/gizmo_imf_sk/
    #cp ./M1e4_R10_S0_T1_B0.1_Res"$s"_n2_sol0.5_42.hdf5 MHD_"$b"_core"$x"/gizmo_imf_sk/
    #cp ./job_submit.sh MHD_"$b"_core"$x"/gizmo_imf_sk/
    #cp ./Config.sh MHD_"$b"_core"$x"/gizmo_imf_sk/
    #cp ./track_job.py MHD_"$b"_core"$x"/gizmo_imf_sk/
    echo MHD_"$b"_core"$x"
    ls -lh ./MHD_"$b"_core"$x"/output/
done

for x in {32,64,128,256,512} ; do
    s=215
    b=1e-3
    #cp ./params_M1e4_R10_S0_T1_B0.1_Res"$s"_n2_sol0.5_42.txt MHD_"$b"_core"$x"/gizmo_imf_sk/
    #cp ./M1e4_R10_S0_T1_B0.1_Res"$s"_n2_sol0.5_42.hdf5 MHD_"$b"_core"$x"/gizmo_imf_sk/
    #cp ./job_submit.sh MHD_"$b"_core"$x"/gizmo_imf_sk/
    #cp ./Config.sh MHD_"$b"_core"$x"/gizmo_imf_sk/
    #cp ./track_job.py MHD_"$b"_core"$x"/gizmo_imf_sk/
    echo MHD_"$b"_core"$x"
    ls -lh ./MHD_"$b"_core"$x"/output/
done
