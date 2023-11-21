i=$PWD 
for d in ../../* ; do
    echo "$d"
    #python clone_gizmo.py --repo_name=gizmo_imf_sk --dest_dir=$d
    cd $d/gizmo_imf_sk
    git reset --hard bc0ed35
    cd $i
    python gizmo_setup.py --repo_dir=$d/gizmo_imf_sk/ --systype=nia
    #mkdir $d/output
    #touch $d/output/cpu.txt
    #cp ../cpu_performance_scripts/track_job.py $d/gizmo_imf_sk/
done
