use feature qw(say);#加载perl的新特性

$outputfolder = "UltraFlex";
mkdir $outputfolder, 0755 or warn "Folder create failed." if ( !-e $outputfolder ); 
$filepath = "J750_Pattern\\";#"input\\"; Jesse@20180411: change J750 .atp folder
opendir FOLDER, $filepath or die "cannot find $filepath";
$is_scan_pat=0; #check the pattern include scan or not

#use for save opcode and opcode located in pattern
$file_opcode_list="opcode_list.txt";
$file_opcode_in_pattern="opcode_in_pattern.txt";
unlink $file_opcode_list       if (-e $file_opcode_list);
unlink $file_opcode_in_pattern if (-e $file_opcode_in_pattern);
my @opcodelist;

#iterate all the files in input folder, and process all the .atp files
my @filelist = readdir(FOLDER);
foreach my $file (@filelist) 
{
	if ( $file =~ /\.atp$/ ) 
	{
		my $filename = $filepath . $file;
		&findopcode( $filename, "$outputfolder\\",$file, &getVectorNum($filename) );   #convert J750 .atp to UltraFlex .atp
		&UltraFlexPatternCompiler ("$outputfolder\\".$file); # compile Ultrafelx ASCII pattern(.atp) to binary pattern(.pat)
	}
}#foreach $file (@filelist)

#couting vector line numbers sub getVectorNum { open READVECTOR,  "<",  $_[0]; 
my $vector_counts=0; my $originStr; while ( defined( $originStr = <READVECTOR> ) 
) { print ''; $vector_counts++ if ($originStr=~/>\s/); } close READVECTOR; 
return $vector_counts; }#getVectorNum

#main function, convert J750 .atp to UltraFlex .atp
sub findopcode
{
	open READ,  "<",  $_[0]; #open J750 .atp for read
	open WRITE, ">", $_[1] . $_[2]; #open a new .atp to convert/write J750 .atp to UlytraFlex
	open WRITE_opcode, ">> $file_opcode_list";
	open WRITE_opcode_location, ">> $file_opcode_in_pattern";
	my $tempt_opcode="";
	
	my $patternnumber=0;
	my $str_line;
	my $outofcolumn = 1;
	my $result="";
	my $originStr="";
	my $orginal_j750;
	my $before="";
	my $pinlist="";
	my $linenumber=0;
	my $subfilename=$_[2];
	my $vector_num=$_[3]; #get the vector counts to determine VM or SRM module.
	$is_scan_pat=0; #check the pattern include scan or not
	$subfilename=~s/\.atp$//;
	$subfilename=~s/-/_/;#replace all illegal characters to support vector module name
	say "$_[0]   Please wait";
	print WRITE_opcode_location "--------------$_[0]--------------\n";
#	my $label_line="";
	my @pattern_header_commets;
	my $flag_header_commets=-1;#indicate the pattern_header_commets
	while ( defined( $originStr = <READ> ) ) 
	{
		chomp($originStr);
		$result="";
		$linenumber++;
		$originStr =~ s/^\s+|\s+$//;
		$orginal_j750=$originStr;
		$str_line=$originStr;
		$tempt_opcode="";#clean tempt opcode
		next if ($originStr eq "");#skip empty line
		
		#process the pattern_header_commets, move the header comments in to vector module
		if($flag_header_commets==-1)
		{ 
			while ( $originStr =~ /^\/\//)
			{
				push(@pattern_header_commets, $originStr);
				$originStr = <READ>;
				chomp($originStr);
				$linenumber++;
				next;
			}
			$flag_header_commets=1;
		}
		
		$is_scan_pat=1 if ($originStr=~/scan_pins\s=/i); #check pattern contain scan or not; scan_pins = {

		#1)check the line is comment or not, if comments just go to write original context directly
		goto WRITE_DIRECTLY if ( $str_line =~ /^\/\/|\/\*/);
		#not comments, do the below process

		#2)check the pattern has scan or not
		if($str_line=~/(\w*):\d,/i) {print WRITE $1 .",\n"; next;} #scan pin setup

		#3)process the vector module header
		if($str_line=~/^vector\s*\(\s*\$tset\s*,/)
		{
			$str_line=~/^vector\s*\(\s*\$tset\s*,(?<pinlist>.*)\)/;
			$pinlist=$+{pinlist};
			#check for VM or SRM(vector line <64>)
			if($vector_num>64)	{print WRITE "vm_vector $subfilename \n";}
			else				{print WRITE "srm_vector $subfilename \n";}
			print WRITE "(\$tset,$pinlist)\n";
			##print WRITE "vm_vector $subfilename (\$tset,$pinlist)\n";
			next;
		}
		#vector context satrt, the pattern_header_commets will be write
		if($str_line=~/^{/)
		{
			print WRITE "{\n";
			if ($#pattern_header_commets>0)
			{
				for (my $i=0; $i<=$#pattern_header_commets; $i++){print WRITE "$pattern_header_commets[$i]\n";}
			}
			next;
		}
		#4)process global subr label
		$originStr=~s/subr\s*// if($originStr=~/^global\s*subr\s*\w+:/i);#global subr -> global
		
#		#process label to combine with vector. due to label in a seperate line
#		if ($originStr=~/:$/){$label_line=$originStr.' '; next;}#label line combine to the next vector
#		$originStr=$label_line.$originStr;#vector combine with previous label
#		$label_line="";#reset label		
		
		#5)check if it's not valid vector
		goto WRITE_DIRECTLY if (!($originStr=~ />/));#valida vector has symbol ">"
		
		#5)check pattern Label and Opcode
		if ( $str_line =~ /^(?<label>.*:)?(?<opcode>.*)>.*;/ or $str_line =~ /^(?<label>\w+\s?:)?(?<opcode>.*)(?<comment>\/\/.*)?/)
		{
			$result = $+{opcode} if ( $+{opcode} );
			if($result ne "" and !($result=~/>/))#skip scan data
			{
				$tempt_opcode=$result;
				$tempt_opcode=~s/\s+$//;
				if($result=~/^repeat.*/){$tempt_opcode =~ s/\d+//;$tempt_opcode=~s/^.*://;}#only for repeat opcode process
			}

		}
		#5)process and convert J750 opcode to the UltraFlex opcode
		if ( $result =~ /mrepeat/ ) {$originStr =~ s/mrepeat/repeat/;} #mrepeat -> repeat
		elsif($result=~/end_module/) {$originStr =~ s/end_module/halt/;} #end_module -> halt
		elsif($result=~/ign/) {$originStr =~ s/\bign\b/mask/;} #ign -> mask
		elsif($result=~/clr_fail/) {$originStr =~ s/clr_fail//; $originStr=$originStr."\/\/clr_fail in J750";} #clr_fail move to comments
		elsif($result=~/set_code/) {$originStr=~/^(set_code\s\d.*)>/; my $match=$1; $match=~s/\s+$//; $originStr =~ s/^.*>/ >/; $originStr=$originStr."//".$match." in J750";} #set_code change to comments
		elsif($result=~/clr_code/) {$originStr =~ s/^.*>/ >/; $originStr=$originStr."\/\/clr_code in J750";} #set_code change to comments
		elsif($result=~/if\s*\(flag\)\s*jump/) {$originStr =~ s/\bflag\b/branch_expr/;} #flag -> branch_expr
		elsif($result=~/clr_flag\s*\(cpuA\)/) {$originStr =~ s/clr_flag/clr_cond_flags/; $originStr=~s/cpuA/cpuA_cond/;}
		elsif($result=~/clr_flag\s*\(fail\)/) {$originStr =~ s/clr_flag/clr_cond_flags/;}
#		elsif($result =~ /set_cpu\s*\(cpuA\)/ ) {$originStr =~ s/set_cpu/set_cpu_cond/; $originStr =~ s/cpuA/cpuA_cond/;}
		elsif($result =~ /exit_loop/ ) {$originStr =~ s/exit_loop/clr_loop/;}
		elsif($result =~ /push/ ) {$originStr =~ s/\bpush\b/push_subr/;}
		elsif($result =~ /call_glo/ ) {$originStr =~ s/call_glo/call globalAddr/;}
		elsif(($result=~/enable/)&&($result=~/none/)) {$originStr =~ s/enable/branch_expr=/;} #enable -> branch_expr		
		elsif($result=~/enable/) {
			$originStr =~ s/enable/branch_expr=/;
			$originStr=~s/cpuA/cpuA_cond/i;
			$originStr=~s/cpuB/cpuB_cond/i;
			$originStr=~s/cpuC/cpuC_cond/i;
			$originStr=~s/cpuD/cpuD_cond/i;			
		} #enable -> branch_expr
		#======process cpuFlag, remove the J750 cpu opcode to comments
		elsif($result=~/cpu/)
		{
			print WRITE "//	TER2018: below vector has opcode: $result\n";#add comments where will remove opcode
			$originStr=substr($originStr,length($result)); #remove the opcode command			
		}
		elsif($result =~ m/\bloop\w\s+(\d+)/ or $result =~ m/set_loop\w\s+(\d+)/) #loop or set_loop... #expand the loop command
		{
			my $loop_count=$1;#get loop counts
			my @loopcontent;
			print WRITE "// TER: Here loop start by loop_count $loop_count\n";
			$originStr=~s/^.*>/ >/;#remove opcode
			push(@loopcontent,$originStr);
			while($originStr=<READ>)
			{
				$linenumber++;
				$originStr=~s/^\s+|\s+$//;
				$originStr='//label '.$originStr.' in J750' if($originStr=~/^\w+:$/);#comment the Label
				last if ($originStr=~/^end_loop\w\s/i);#special case like control bit: end_loopA Start, stv > tset
				push(@loopcontent,$originStr);
			}
			my $stv_exist="";
			$stv_exist="stv" if ($originStr=~/\bstv/);
			$originStr=~s/^.*>/ >/;#remove opcode and control bit
			$originStr=$stv_exist.$originStr; #setback stv if vectort has stv control bit
			push(@loopcontent,$originStr);
			for (my $looping=0;$looping< $loop_count;$looping++)#expand the loop command			
			{
				for(my $i=0;$i<($#loopcontent+1);$i++) #print vectors
				{
					print WRITE "// TER: Here loop end by loop_count $loop_count\n" if (($looping== $loop_count-1) and ($i==$#loopcontent));
					print WRITE " $loopcontent[$i] \n";
				}
			}
			next;#jump to next read line
		} #elsif($result =~ m/\bloop\w\s+(\d+)/ or $result =~ m/set_loop\w\s+(\d+)/) #loop or set_loop... #expand the loop command
		else{} #nothing to do
		#===========save opcode
		if ($tempt_opcode ne "")
		{
			my $exist_cnt=(grep /^$tempt_opcode$/, @opcodelist);
			if ($exist_cnt==0)
			{
				push( @opcodelist, $tempt_opcode );
				print WRITE_opcode_location "$linenumber:  ";
				print WRITE_opcode_location "$orginal_j750\n";
				print WRITE_opcode "$tempt_opcode\n";				
			}			
		}					
		#nothing to process, just write original context directly
		WRITE_DIRECTLY:	print (WRITE "$originStr\n");
	}
	
	#close files
	close READ;
	close WRITE;
	close READTEMPT;
}

sub UltraFlexPatternCompiler()
{
	my $input_file=$_[0];#"UltraFlex_SRM_VM_Dummy.atp ";
	#$output="-output ";
	my $pinmap="-pinmap_workbook ";
	my $digital_inst="-digital_inst ";
	my $opcode_mode="-opcode_mode ";
	my $scan_type="-scan_type ";
	my $save_comments="-comments ";
	
	$pinmap=$pinmap . "Pinmap.txt "; #specified the pinmap file
	$digital_inst=$digital_inst . "HSDMQ "; #specified the digital instrument
	$opcode_mode=$opcode_mode ."single "; #specififed the timing mode
	$scan_type=$scan_type."x2 " if $is_scan_pat;#specified the scan type in 2x for scan pattern
	
	my $switches=$pinmap.$digital_inst.$opcode_mode;
	if($is_scan_pat){$switches=$switches.$scan_type.$save_comments;	}
	else			{$switches=$switches.$save_comments;}
	
	my $my_command="apc ".$input_file ." " .$switches;
	
	#system("apc -stdin -output bar.pat");
	system($my_command);#invoke the pattern compiler by command-line interface: apc input-ascii-file(s) [switches]
}