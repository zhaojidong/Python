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

#traversal the J750 Folder
J750_atp_list=os.listdir(J750_dir)
def findopcode():
    reapt_flag = 0
    halt_flag = 0
    scan_setup_flag = 0
    line_no = 0  # line number
    atp_file_name_flag = 0
    vector_num_flag=0
    bracket_flag=0
    reg=''
    for atp_file in J750_atp_list:
        vector_num_flag = 0
        UltraAtpPath = os.path.join(os.path.abspath('..'), 'UltraFlex', atp_file)
        if re.match(r'.*\.atp', atp_file):
            print(atp_file)
            vector_num = -1  # statistics the vector num
            for vector_num, line in enumerate(open(os.path.join(J750_dir, atp_file), 'rU')):
                pass
                vector_num += 1
            with open(os.path.join(J750_dir, atp_file), 'r') as fp:
                UltraAtpPath_fp = open(UltraAtpPath, 'w+')
                lines=[]    #insert at the specofied line
                for line in UltraAtpPath_fp:
                    lines.append(line)
                atp_line = fp.readline()  # readline读完本行就会自动定位到下一行  一直读到没有下一行
                while atp_line:
                    line_no = line_no + 1
                    if re.match(r'import tset\s+[\d\w\s]', atp_line):
                        #get the string after the import tset---start
                        tset_label=re.sub(r'import tset\s+','',atp_line)
                        tset_label = re.sub(r';', '', tset_label)
                        tset_label=tset_label.replace('\n','')#delet \n
                        reg = re.compile(r'\s+>\s+' + tset_label)
                        # get the string after the import tset---end
                        lines.insert(0, atp_line)  # insert at the first row
                        s = ''.join(lines)
                        UltraAtpPath_fp = open(UltraAtpPath, 'w')
                        UltraAtpPath_fp.write(s)
                    if vector_num_flag == 0:
                        atp_file = re.sub(r'\.atp$', '',atp_file)
                        if (vector_num > 64):
                            lines.insert(1, 'vm_vector ' + atp_file + '\n')  # insert at the second row
                        else:
                            lines.insert(1, 'vm_vector ' + atp_file + '\n')
                        s = ''.join(lines)
                        UltraAtpPath_fp = open(UltraAtpPath, 'w')
                        UltraAtpPath_fp.write(s)
                        vector_num_flag = 1
                    if re.match(r'\s*vector\s+\(\s*\$tset\s*\,', atp_line):
                        pin_line = re.sub(r'\s*vector\s+\(\s*\$tset\s*\,', '($tset ', atp_line)
                        lines.insert(2, pin_line)  # insert at the first row
                        s = ''.join(lines)
                        UltraAtpPath_fp = open(UltraAtpPath, 'w')
                        UltraAtpPath_fp.write(s)
                        # UltraAtpPath_fp.write(pin_line)
                        if bracket_flag == 0:
                            lines.insert(3, '{\n')  # insert at the first row
                            s = ''.join(lines)
                            UltraAtpPath_fp = open(UltraAtpPath, 'w')
                            UltraAtpPath_fp.write(s)
                            bracket_flag = 1
                    if re.match(r'//', atp_line):
                        lines.insert(5, atp_line)
                        s = ''.join(lines)
                        UltraAtpPath_fp = open(UltraAtpPath, 'w')
                        UltraAtpPath_fp.write(s)
                    if re.match(r'start_label\s+', atp_line):
                        UltraAtpPath_fp.write(atp_line)
                    '''
                    write opcode_list&opcode_in_pattern&UltraAtpPath-----Start!!!
                    '''
#match repeat
                    if re.match(r'\s*repeat\s+\d+\s+\>', atp_line):
                        if reapt_flag == 0:
                            reapt_flag = 1
                            opcode_list_fp.write('repeat\n')#write into opcode_list file
                            opcode_in_pattern_fp.write(
                                str(line_no) + ":" + " " + atp_line)  # String concatenation and output
                        UltraAtpPath_fp.write(atp_line)
#match halt
                    if re.match(r'\s*halt\s+\>\s*', atp_line):
                        if halt_flag == 0:
                            halt_flag = 1
                            opcode_list_fp.write('halt\n')  # write opcode to opcode_list
                            opcode_in_pattern_fp.write(
                                str(line_no) + ":" + " " + atp_line)  # write opcode and pattern to opcode_in_pattern
                        UltraAtpPath_fp.write(atp_line)
#match sacn_setup
                    if re.match(r'\s*scan_setup\s+\>\s*', atp_line):
                        if scan_setup_flag == 0:
                            scan_setup_flag = 1
                            opcode_list_fp.write('scan_setup\n')
                            opcode_in_pattern_fp.write(str(line_no) + ":" + " " + atp_line)
                        UltraAtpPath_fp.write(atp_line)
#no opcode,match tset name
                    if re.match(reg,atp_line):
                        modify_line=re.sub(r'\s+>\s+','> ',atp_line)
                        UltraAtpPath_fp.write(modify_line)
#match /* multi-line matching
                    '''
                    if re.match(r'^/\*\s*',atp_line):
                        UltraAtpPath_fp.write(atp_line)
                        atp_line = fp.readline()
                        while re.match(r'\*/',atp_line) == None:
                            UltraAtpPath_fp.write(atp_line)
                            atp_line = fp.readline()
                        else:
                            UltraAtpPath_fp.write(atp_line)
                    '''
                    if (0==atp_line.find('/*'))&(0==atp_line.find('*/')):
                        UltraAtpPath_fp.write(atp_line)
                    elif (0==atp_line.find('/*'))&(-1==atp_line.find('*/')):
                        UltraAtpPath_fp.write(atp_line)
                        atp_line = fp.readline()
                        while atp_line.find('*/') == -1:
                            UltraAtpPath_fp.write(atp_line)
                            atp_line = fp.readline()
                        else:
                            UltraAtpPath_fp.write(atp_line)
#match //
                    if re.match(r'//\s*', atp_line):
                        UltraAtpPath_fp.write(atp_line)

                    if re.match(r'^\n',atp_line):
                        re.sub(r'\n', '}', atp_line)
                        UltraAtpPath_fp.write(atp_line)
                    '''
                    write opcode_list&opcode_in_pattern&UltraAtpPath-----End!!!
                    '''
                    if atp_file_name_flag == 0:
                        opcode_in_pattern_fp.write("--------------------" + atp_file + "--------------------" + '\n')
                        atp_file_name_flag = 1
                    atp_line = fp.readline()
                UltraAtpPath_fp.write('}')
                atp_file_name_flag = 0


def ConvertPat():
    vector_num_flag=0
    bracket_flag=0
    for atp_file in J750_atp_list:
        UltraAtpPath=os.path.join(os.path.abspath('..'),'UltraFlex',atp_file)
        if re.match(r'.*\.atp', atp_file):
            vector_num = -1#statistics the vector num
            for vector_num, line in enumerate(open(os.path.join(J750_dir, atp_file), 'rU')):
                pass
                vector_num += 1
            with open(os.path.join(J750_dir, atp_file), 'r') as fp:
                UltraAtpPath_fp = open(UltraAtpPath, 'w+')
                lines=[]    #insert at the specofied line
                for line in UltraAtpPath_fp:
                    lines.append(line)
                atp_line = fp.readline()  # readline读完本行就会自动定位到下一行  一直读到没有下一行
                while atp_line:
                    if re.match(r'import tset\s+[\d\w\s]',atp_line):
                        lines.insert(0,atp_line)  #insert at the first row
                        s=''.join(lines)
                        UltraAtpPath_fp = open(UltraAtpPath, 'w')
                        UltraAtpPath_fp.write(s)
                    if vector_num_flag==0:
                        if (vector_num > 64):
                            lines.insert(1, 'vm_vector ' + atp_file+ '\n')  #insert at the second row
                        else:
                            lines.insert(1, 'vm_vector ' + atp_file+ '\n')
                        s = ''.join(lines)
                        UltraAtpPath_fp = open(UltraAtpPath, 'w')
                        UltraAtpPath_fp.write(s)
                        vector_num_flag=1
                    if re.match(r'\s*vector\s+\(\s*\$tset\s*\,',atp_line):
                        pin_line=re.sub(r'\s*vector\s+\(\s*\$tset\s*\,','($tset ',atp_line)
                        lines.insert(2,pin_line)  #insert at the first row
                        s=''.join(lines)
                        UltraAtpPath_fp = open(UltraAtpPath, 'w')
                        UltraAtpPath_fp.write(s)
                        #UltraAtpPath_fp.write(pin_line)
                        if bracket_flag==0:
                            lines.insert(3, '{\n')  # insert at the first row
                            s = ''.join(lines)
                            UltraAtpPath_fp = open(UltraAtpPath, 'w')
                            UltraAtpPath_fp.write(s)
                            bracket_flag=1
                    if re.match(r'//',atp_line):
                        lines.insert(5,atp_line)
                        s = ''.join(lines)
                        UltraAtpPath_fp = open(UltraAtpPath, 'w')
                        UltraAtpPath_fp.write(s)
                    if re.match(r'start_label\s+',atp_line):
                        UltraAtpPath_fp.write(atp_line)
                    atp_line = fp.readline()

def AtpToPat():
    print('Pat')
    print('')
    print('')
findopcode()
#ConvertPat()
print("Finished!")


