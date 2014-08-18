# 
# fffchk.py
#
#   Program to validate the contents of a "flat" file.  It takes the file names
#   and record layout specification from a configuration file that is either 
#   specified as a parameter or just exists as fileconf.ini in the 
#   current directory.
#
#   Usage:
#     fffchk.py [-h] [-i <input file>] [-r <report file>] [-c <config file>]
#

import sys, argparse, configparser

def get_configs (cdict):
#
# Takes the configuration settings dictionary as a
# parameter and sets the configuration values in the 
# dictionary from the settings in the configuration file
# which is determined from the 'config' setting in the
# dictionary that is passed. 
#

    configs = configparser.ConfigParser()
    try: 
        configs.read(cdict['config'])
    except: 
        print (
            "Cannot open config file {0} -- continuing with program defaults".
            format(cdict['config'])
            )
        
    # get valudes from config file parser, 
    # the settings are irrespective of section
    for sections in configs.sections():
        for settings in configs[sections]:
            cdict[settings] = configs[sections][settings]
    
    # Values for "fields" and "length" must be numeric and
    # "reqflds" must be a comma separated numeric list
    if not cdict['fields'].isdigit():
        print("Invalid value for 'fields' in configuration file.")
        print("Setting must be a number; continuing with default value of 1")
        cdict['fields'] = 1
        
    if cdict['length'] and not cdict['length'].isdigit():
        print("Invalid value for 'length' setting must be a number!")
        print("Setting must be a number; no record length checking will be done.")
        cdict['length'] = ""
        
    if cdict['reqflds']:
        required_fields = []
        try:
             for f in cdict['reqflds'].split(","):
                 required_fields.append(int(f))        
        except:
            print ("Required fields 'reqflds' setting must be list of comma-separated numbers")
            print ("No checking will be performed for required fields.")
            required_fields = ""
        cdict['reqflds'] = required_fields
   
	
def validate_file (config_dict):
# 
#  File validation routine that uses the settings in the
#  configuration dictionary to check the contents of the 
#  file.  The checks that can be specified include:
#  number of fields, required fields populated (starting
#  with 1 as the first field) and record length
#
    print ("processing input file " + config_dict['input'])    

    # Expecting 'input' file, 'report' file, and 'delimiter' to have
    # values in the config dictionary
    data_file = open(config_dict['input'],'r')
    report_file = open(config_dict['report'],'w')

    rec_count = 0
    flagged_rec_count = 0

    for line in data_file :
        rec_flagged = False
        rec_count += 1
        
        # Check record length if specified
        if config_dict['length']:
            line_length = len(line) 
            if line_length != int(config_dict['length']):
                 rec_flagged = True
                 report_file.write(
                     "{0} characters in record #{1} expecting {2} characters.\n".format(
                         line_length, 
                         rec_count, 
                         config_dict['length']
                         ))
                         
        # Check number of fields
        if config_dict['fields']:
            fields = line.split(config_dict['delimiter'])
            if len(fields) != int(config_dict['fields']) :
                rec_flagged = True
                report_file.write("{0} fields in record #{1} expecting {2} fields.\n".format(
                    len(fields), 
                    rec_count, 
                    config_dict['fields']
                    )
                ) 
        
        # Check required fields to ensure they have values
        if config_dict['reqflds']:
            for f in config_dict['reqflds']:
                if not fields[f-1]:
                    rec_flagged = True
                    report_file.write("Field {0} in record #{1} must have a value.\n".format(
                        f, 
                        rec_count 
                        )
                    )

        if rec_flagged :
            flagged_rec_count += 1
                
    print("{0} records processed".format(rec_count))
    print("{0} records flagged for errors".format(flagged_rec_count))
    if flagged_rec_count > 0:
        print ("See details in report file " + config_dict['report'])     
    
def main(argv_args):
#
#  Routine for main program flow.  Checks the argument array 
#  passed as a parameter), sets configuration defaults, gets 
#  config file settings and validate the file. 
#   

    print ("Starting...\n")
 
    # Set config defaults.  Order below is relevant. 
    # Priority is: 
    #    1) command line args, which override
    #    2) config file items, which override
    #    3) program defaults (set in dictionary init).  

    config_dictionary = { 'input' : "input.txt",
	                     'report': "output.txt",
                         'config': argv_args.cfile,
		                 'delimiter' : ",",
                         'fields' : "1",
                         'reqflds' : "",
                         'length' : "" 
				        }
    get_configs(config_dictionary)   
    if argv_args.ifile:
        config_dictionary['input'] = argv_args.ifile
    if argv_args.rfile:
        config_dictionary['report'] = argv_args.rfile

    validate_file(config_dictionary)

    print ("Done.\n")

#
# Body of program - takes argument array and calls "main" routine.
#
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Flat file format check")
    arg_parser.add_argument('-i','--ifile',help='the input file to check')
    arg_parser.add_argument('-r','--rfile',help='the report output file')
    arg_parser.add_argument('-c','--cfile',default='fileconf.ini',help='the configuration file to use')
    args = arg_parser.parse_args()
    main(args)