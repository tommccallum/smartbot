<html>
<head>
<title>Innogen Radio</title>
</head>
<body>
<h1>Innogen Radio</h1>

<?php

$output = shell_exec("df -h | grep \"/dev/root\" | awk '{print \$5}' | sed \"s/%//\"");
if ( $output < 10 ) {
	echo "<div class='alert bad'>You are running out of diskspace, tell Dad!</div>";
} else {
	echo "<div class='alert ok'>You are ok on diskspace, keep calm and carry on!</div>";
}

?>

<form method=POST action="addprogram.php">
<label for="name">Programme Name:</label>
<input type="text" name="name" placeholder="Radio 2 programme name">
<input type="submit" name="Add" value="Add">
</form>

<?php

function get_duration($file) {
	ob_start();
	passthru("/usr/bin/ffmpeg -i \"{$file}\" 2>&1");
	$metadata = ob_get_contents();
	ob_end_clean();
	$search='/Duration: (.*?),/';
	$duration=preg_match($search, $metadata, $matches, PREG_OFFSET_CAPTURE, 3);
	return $matches[1][0]; 
}

function get_radio_programs() {
	$files = glob("./radio/*.m4a");
	sort($files);
	return $files;
}

function gen_programme_table($files) {
	$html = "";
	foreach ($files as $file ) {
		$size = filesize($file);
		$filename = basename($file);
		$lastmodified = date("F d Y H:i", filemtime($file));
		$path = $file;
#		$duration = get_duration($file);
		$name = preg_replace("/_m[\d\w]+_original.m4a/", "", $filename );
		$name = preg_replace("/_/", " ", $name );
		$actions = array( "<a href='play.php?name=".(base64_encode($path))."'>Play</a>",
					"<!-- <a href='delete.php?name=".(base64_encode($path))."'>Delete</a> -->" );
		$html = $html."<tr><td>$lastmodified</td><td>$name</td><td>".join("&nbsp;|&nbsp;",$actions)."</td></tr>\n";
	}
	return $html;
}

?>
<table>
<thead>
<tr><th>Last Modified</th><th>Show</th><th>Actions</th></tr>
</thead>
<tbody>
<?= gen_programme_table(get_radio_programs()); ?>
</tbody>
</table>

<h1>Live Streams</h1>

<p>These take about 1 minute to tune in.</p>

<ul>
<li><a href="play.php?name=<?= base64_encode("http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p") ?>">BBC Radio 2</a></li>
<li><a href="play.php?name=<?= base64_encode("http://listen1.mixlr.com/d6b566b5424ddd324b59b3bb21132217") ?>">Big Dog Radio</a></li>
</ul>
</body>
</html>
