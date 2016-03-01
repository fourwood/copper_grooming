#!/usr/bin/env python3
import collections
import datetime
import json
import re
import urllib.request
import urllib.error

def main():
    out_filename = 'groomed_runs.json'

    report_url = 'http://www.coppercolorado.com/winter/the_mountain/dom/snow.html'
    request = urllib.request.Request(report_url)
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.URLError as error:
        if hasattr(error, 'reason'):
            print("Failed to connect to server.")
            print("Reason: ", error.reason)
        elif hasattr(error, 'code'):
            # Received an HTTP error code from the server (e.g. 404)
            print("The server couldn't fulfill the request.")
            print("Error code: ", error.code)
    else:
        # Everything is fine

        #TODO: Add lift section?

        ### Grab the grooming report, note the date and pull out which runs are groomed
        html = [line.decode() for line in response]

        today = datetime.date.today()
        cur_month_name = today.strftime("%B")
        parsed_date_str = [s for s in html if cur_month_name in s][0].strip()
        date = datetime.datetime.strptime(parsed_date_str, "%A, %B %d, %Y %I:%M %p")
        date_str = date.strftime('%Y/%m/%d')

        # Grab the mid- and upper-mountain base numbers
        base_idx = [i for i,x in enumerate(html) if '<th colspan="2">Snow Depths</th>' in x][0]
        mid_base_idx = base_idx + 7
        upper_base_idx = base_idx + 8
        mid_base = float(re.findall("\d+\.\d+", html[mid_base_idx])[0])
        upper_base = float(re.findall("\d+\.\d+", html[upper_base_idx])[0])

        # Grab the new snowfall totals
        new_snow_24hr_idx = [i for i,x in enumerate(html) if '<td colspan="6">24 hrs</td>' in x][0]
        new_snow_24hr_idx += 3
        new_snow_24hr = float(re.findall("\d+\.\d+", html[new_snow_24hr_idx])[0])

        new_snow_overnight_idx = [i for i,x in enumerate(html) if '<td></td><td><strong>Overnight</strong></td><td></td>' in x][0]
        new_snow_overnight_idx += 3
        new_snow_overnight = float(re.findall("\d+\.\d+", html[new_snow_overnight_idx])[0])

        # Find 'groomed.gif' in the HTML, subtract 1 to get the line before it,
        # which contains the run name.
        groomed_run_idx = [i-1 for i,x in enumerate(html) \
                if ('groomed.gif' in x) or ('groomed_noon.gif' in x)]

        # Then strip out the HTML and get the text in between...
        run_names_html = [html[i].strip() for i in groomed_run_idx]
        run_names = [s.split('<td class="title">')[-1].split("</td>")[0] for s in run_names_html]

        # And return a unique list.
        run_names = list(set(run_names))

        ### Open up the JSON file we're saving it all in and add the date to all
        ### the matching groomed runs
        try:
            out_file = open(out_filename, 'r')
        except FileNotFoundError as e:
            # If the data file can't be found, make an empty template.
            json_str = '{ \
               "new_snow_overnight": {}, \
               "new_snow_24hr": {}, \
               "mid_base": {}, \
               "upper_base": {}, \
               "runs": {} \
               }'
            json_data = json.loads(json_str, object_pairs_hook=collections.OrderedDict)
        else:
            json_data = json.load(out_file, object_pairs_hook=collections.OrderedDict)
            out_file.close()

        # Process new snowfall
        new_snow_24hr_dict = json_data['new_snow_24hr']
        if date_str not in new_snow_24hr_dict:
            new_snow_24hr_dict[date_str] = new_snow_24hr

        new_snow_overnight_dict = json_data['new_snow_overnight']
        if date_str not in new_snow_overnight_dict:
            new_snow_overnight_dict[date_str] = new_snow_overnight

        # Process snow base
        mid_base_dict = json_data['mid_base']
        if date_str not in mid_base_dict:
            mid_base_dict[date_str] = mid_base

        upper_base_dict = json_data['upper_base']
        if date_str not in upper_base_dict:
            upper_base_dict[date_str] = upper_base

        # Process the runs
        runs = json_data['runs']
        for run in run_names:
            if run in runs:
                #print("Run {0} exists".format(run))
                cur_data = runs[run]
                if date_str not in cur_data:
                    cur_data.append(date_str)
            else:
                #print("Run {0} doesn't exist".format(run))
                runs[run] = list([date_str])
        json_data['runs'] = collections.OrderedDict(sorted(runs.items(),
                key=lambda t: t[0]))

        # Aaaand save to disk.
        with open(out_filename, 'w') as out_file:
            json.dump(json_data, out_file, indent=4)

if __name__ == "__main__":
    main()
