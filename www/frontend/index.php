<html>
<head>
<title>TMPL: Topic Modeling in PL</title>
</head>
<body>
<center>
  <h1>TMPL: Topic Modeling in PL</h1>
  <h2>Tracking the flow of ideas through the programming languages literature</h2>
  <h3>
    <a href="http://www.cs.pomona.edu/~michael/">Michael Greenberg</a>,
    <a href="http://www.cs.tufts.edu/~kfisher/Kathleen_Fisher/Home.html">Kathleen Fisher</a>, and
    <a href="http://www.cs.princeton.edu/~dpw/">David Walker</a>
  </h3>
</center>

<p>Check out our <a href="http://snapl.org/2015/">SNAPL</a> paper,
titled <a href="http://www.cs.pomona.edu/~michael/papers/snapl2015.pdf">Tracking
the flow of ideas through the programming languages
literature</a>. We've put up some of
the <a href="figures.php">figures</a> from the paper (and more recent
work) in a larger format. We've also built a tool to help search for
related work using the topic models we built. You can also look at our
analysis of <a href="http://www.cs.pomona.edu/~michael/popl15/">POPL
2015</a>.</p>

<p>Upload a PDF and we'll give you the 10 most closely related papers
according to the topic model we've built on the abstracts of POPL and
PLDI.</p>

<form id="upload" enctype="multipart/form-data" action="index.php" method="POST">
    <input type="hidden" name="MAX_FILE_SIZE" value="41943040" />
    <input name="userpdf" type="file" />
    <input type="submit" value="Upload PDF" />
</form>

<?php
$upload_dir = "/n/fs/tmpl/uploads";
$backend_dir = "/n/fs/tmpl/backend";

if ($_FILES['userpdf']['error'] == UPLOAD_ERR_OK &&
    is_uploaded_file($_FILES['userpdf']['tmp_name'])) {
   // okay, we have the file

   echo "<p>Processing " . $_FILES['userpdf']['name'] . "...</p>";
   echo "<pre>";
   $pdf = tempnam($upload_dir, "doc-");
   if (move_uploaded_file($_FILES['userpdf']['tmp_name'],$pdf)) {
      chdir($backend_dir);
      putenv('PATH=/n/fs/tmpl/.local/bin:/n/fs/tmpl/lda-c-dist:$PATH');
      putenv('PYTHONIOENCODING=utf8');
      
      system("/usr/bin/python infer.py $pdf 2>&1");
   }
   echo "</pre>";
} else if (in_array($_FILES['userpdf']['error'],
                    array(UPLOAD_ERR_INI_SIZE, UPLOAD_ERR_FORM_SIZE))) {
   echo "<p>Your PDF was too big. Sorry!</p>";
}
?>

<center>
  <a href="http://www.textfiles.com/underconstruction/"><img src="construction.gif" /></a>
  <p><b>Coming soon:</b> your choice of fancier topic models!</p>
</center>
</body>
</html>
