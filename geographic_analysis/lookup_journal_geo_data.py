#!/user/bin/env python3
# This script is intended for PBS jobs to extract geo data from a CSV containing an IP column

import geoip2
import geoip2.database
import os
import re


def main():
    working_dir = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/geo_data"
    raw_ip_filepath = os.path.join(working_dir, "journal_ip_raw.csv")
    geo_info_added_filepath = os.path.join(working_dir, "journal_geo_data.csv")
    
    city_database_filepath = "/home/srivbane/shared/caringbridge/data/derived/geolite2/GeoLite2-City_20190813/GeoLite2-City.mmdb"
    reader = geoip2.database.Reader(city_database_filepath)
    print("Reader initialized. Beginning lookup.")
    
    not_found_count = 0
    with open(raw_ip_filepath, 'r') as infile:
        with open(geo_info_added_filepath, 'w') as outfile:
            for i, line in enumerate(infile):
                tokens = line.strip().split(",")
                if len(tokens) != 6:
                    raise ValueError(f"Too many values to unpack: {line}")
                user_id, ip, site_id, journal_oid, created_at, updated_at = tokens
                try:
                    g = reader.city(ip)
                except geoip2.errors.AddressNotFoundError:
                    not_found_count += 1
                    outfile.write(f"{user_id},{site_id},{created_at},NOT_FOUND,,,,,,\n")
                    continue
                country = g.country.iso_code
                subdiv_count = len(g.subdivisions)
                state = g.subdivisions.most_specific.iso_code
                city = g.city.name
                lat = g.location.latitude
                long = g.location.longitude
                acc_radius = g.location.accuracy_radius

                outfile.write(f"{user_id},{site_id},{created_at},{country},{subdiv_count},{state},\"{city}\",{lat},{long},{acc_radius}\n")
                
                if i % 100000 == 0:
                    print(f"Processed {i} lines. {not_found_count} IPs not found so far.")
            print(f"Finished processing {i} lines. {not_found_count} IPs not found.")

                  
if __name__ == "__main__":
    main()
