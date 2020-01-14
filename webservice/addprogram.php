<html>
<body>
<h1>Adding new programme</h1>
<?php

$file="/home/pi/get_iplayer/programs";
if ( isset($_POST['name']) ) {
	$name = $_POST['name'];
	if ( $name != "*" ) {
		$contents = preg_split("/\n/", file_get_contents($file));
		$cmp = strtolower($name);
		$result = "";
		foreach( $contents as $c ) {
			if ( strtolower($c) == $cmp ) {
				$result = "Programme is already being downloaded.";
				break;
			} else if (strtolower($c) == '"'.$cmp.'"') {
				$result = "Programme is already being downloaded.";
                                break;
			}
		}
		if( strlen($result) == 0 ) {
			$fh = fopen($file, "a");
			fwrite( $fh, '"'.$name."\"\n" );
			fclose( $fh );
			$result = "Programme added to file.";
		}
	} else {
		$result = "Cannot set this to asterisk (*).";
	}
} else {
	$result = "No new programme selected.";
}
$content = file_get_contents($file);
?>

<div class="alert">
	<?=$result ?>
</div>

<div>
	<pre>
<?=$content ?>
	</pre>
</div>

<div><a href="index.php">Go back to front page</a></div>
</body>
</html>

