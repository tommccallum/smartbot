<html>
<head>
<meta http-equiv="refresh" content="10; url=/index.php">
</head>
<body>
<p>This page will refresh and go back to the index in 10 seconds.</br>
To view the log look at radio.log.</p>
<?php

if ( !isset($_GET['name']) ) {
	exit(0);
}
$output = shell_exec("ps aux | grep mplayer | grep -v 'grep'");
echo "<ul>";
echo "<li>Currently playing</li>";
echo("<pre>$output</pre>");
shell_exec("killall mplayer");
echo "<li>After killing existing playing</li>";
$output = shell_exec("ps aux | grep mplayer | grep -v 'grep'");
echo("<pre>$output</pre>");
$name = $_GET['name'];
$programme = base64_decode($name);
echo "<li>Playing programme $programme</li>";
shell_exec("/usr/bin/mplayer --really-quiet $programme > radio.log 2>&1 &");
echo "<li>Currently playing</li>";
$output = shell_exec("ps aux | grep mplayer | grep -v 'grep'");
echo("<pre>$output</pre>");
echo "</ul>";
?>
</body>
</html>


