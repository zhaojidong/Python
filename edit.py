#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os,re,sys

dir=r'D:\Project_Test\Python\J750_to_Ultra_compiler'
make_dir=r'D:\Project_Test\Python\J750_to_Ultra_compiler\UltraFlex'
J750_dir=r'D:\Project_Test\Python\J750_to_Ultra_compiler\J750_Pattern'
opcode_list=r'D:\Project_Test\Python\J750_to_Ultra_compiler\opcode_list.txt'
opcode_in_pattern=r'D:\Project_Test\Python\J750_to_Ultra_compiler\opcode_in_pattern.txt'
#os.rmdir(make_dir)

if os.path.exists(make_dir):
    print("The folder already exists!")
else:
    os.mkdir(make_dir,777)  #mode=777  if mode=0777 will be error
    print("The folder created successfully!")

if os.path.exists(J750_dir):
    os.chdir(J750_dir)
#use for save opcode and opcode located in pattern
opcode_list_fp=open(opcode_list,'w')
opcode_in_pattern_fp=open(opcode_in_pattern,'w')

'''
traversal the J750 Folder
'''
reapt_flag = 0
halt_flag = 0
scan_setup_flag=0
line_no=0 #line number
atp_file_name_flag = 0

J750_atp_list=os.listdir(J750_dir)
for atp_file in J750_atp_list:
    #print(os.path.join(J750_dir,atp_file))
    if re.match(r'.*\.atp',atp_file):
        print(atp_file)
        with open(os.path.join(J750_dir,atp_file),'r') as fp:
            #fp.write('Ansel------------------------1234567')
            atp_line = fp.readline()#readline读完本行就会自动定位到下一行  一直读到没有下一行
            while atp_line:
                #print(atp_line)
                line_no=line_no+1
                if reapt_flag==0:
                    if re.match(r'\s*repeat\s+\d+\s+\>',atp_line):
                        reapt_flag=1
                        opcode_list_fp.write('repeat\n')
                        opcode_in_pattern_fp.write(str(line_no) + ":" + " " + atp_line)  # String concatenation and output
                if halt_flag==0:
                    if re.match(r'\s*halt\s+\>\s*',atp_line):
                        halt_flag=1
                        opcode_list_fp.write('halt\n')#write opcode to opcode_list
                        opcode_in_pattern_fp.write(str(line_no) + ":" + " " + atp_line)#write opcode and pattern to opcode_in_pattern
                if scan_setup_flag==0:
                    if re.match(r'\s*scan_setup\s+\>\s*',atp_line):
                        scan_setup_flag=1
                        opcode_list_fp.write('scan_setup\n')
                        opcode_in_pattern_fp.write(str(line_no) + ":" + " " + atp_line)

                if atp_file_name_flag == 0:
                    opcode_in_pattern_fp.write("--------------------" + atp_file + "--------------------" + '\n')
                    atp_file_name_flag = 1
                atp_line = fp.readline()
            atp_file_name_flag = 0


print("Finished!")
#def findopcode():




