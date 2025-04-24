#!/bin/bash

# Directory containing the files in subdir atm, bry, clm (e.g. output dir)
base_dir="$1"

# Function to increment date to see if they are consecutive 
increment_date() {
    date -d "$1 + 1 day" +"%Y%m%d"
}

for dir in atm bry clm atm70 atm71; do
    base_name="m00"
    if [ "$dir" == "atm70" ]; then
        base_name="m70"
        dir="atm"
    elif [ "$dir" == "atm71" ]; then
        base_name="m71"
        dir="atm"
    fi

    # Extract dates from filenames
    extracted_dates=()
    for file in "$base_dir/$dir/norkyst_$dir"_*"$base_name.nc"; do
        filename=$(basename "$file")
        date_part=$(echo "$filename" | grep -oP '\d{8}')
        extracted_dates+=("$date_part")
    done

    # Sort the extracted dates
    sorted_dates=($(printf "%s\n" "${extracted_dates[@]}" | sort))
    # We have data from
    start_date="${sorted_dates[0]}" # 20250213 or 14
    today_date=$(date +%Y%m%d)

    # Loop through the dates and count nr of dates
    current_date=$start_date
    i=0
    all_dates=()
    while [[ "$current_date" -le "$today_date" ]]; do
        all_dates+=("$current_date")
        current_date=$(increment_date "$current_date")
        ((i=i+1))
    done

    # Compare number of dates
    if [ "$i" != "${#sorted_dates[@]}" ]; then
        # If nr. dates not equal find the missing dates
        missing_dates=()
        for date in "${all_dates[@]}"; do
            found=0
            for file_date in "${sorted_dates[@]}"; do
                if [ "$file_date" == "$date" ]; then 
                    found=1
                    break
                fi
            done
            if [ $found -eq 0 ] && [ "$date" != "20250318" ] && [ "$date" != "20250319" ]; then
                # exception for 18 and 19.03.2025 which are always going to be missing
                missing_dates+=("$date")
                file_missing="norkyst_${dir}_${date}T00Z${base_name}.nc"
                # Write out the missing files
                printf "%s : Missing date %s (e.g. %s)\n" "$dir" "$date" "$file_missing"  >> /lustre/storeB/project/fou/hi/foccus/forcing_warning.out 
                printf "%s : Missing date %s (e.g. %s)\n" "$dir" "$date" "$file_missing"
                # The file does not exist
                #ls -l "$base_dir/$dir/$file_missing"
                # make a list to rsync from  
                echo "inkul7832@ppi-r8login-a2.int.met.no:/lustre/storeA/project/metproduction/products/norkyst_v3/$base_name/$file_missing" >> /lustre/storeB/project/fou/hi/foccus/${dir}_rsync.txt

            fi
        done
    #else
    #    echo "$dir : no missing files!"
    fi

    # finalize rsync of missing files
    #rsync --dry-run -avz --progress -e 'ssh -i /home/inkul7832/.ssh/id_rsa_lumi' --files-from=/lustre/storeB/project/fou/hi/foccus/${dir}_rsync.txt $base_dir/$dir
    #echo "rsync --dry-run -avz --progress -e 'ssh -i /home/inkul7832/.ssh/id_rsa_lumi' --files-from=/lustre/storeB/project/fou/hi/foccus/${dir}_rsync.txt $base_dir/$dir"
done



