<html>
<head>
</head>
<body>
<?php

if ( !isset($_GET['name']) ) {
	echo("Nothing to remove.");
	exit(0);
}
$nm = base64_decode($_GET['name']);
if ( strpos( $nm, "*" ) === false && 
	strpos($nm, "..") === false &&
	preg_match( "/^.\/radio\/\w/", $nm ) === 1 ) {
	if ( file_exists($nm) ) {
		unlink($nm);
	}
	if ( file_exists($nm) ) {
		echo("Failed to remove file '$nm'. <a href='index.php'>Go back</a>");
	} else {
		echo("Successfully removed file '$nm'. <a href='index.php'>Go back</a>");
	}
} else {
	echo("File fails checks for valid filename: $nm");
}
?>

</body>
</html>


