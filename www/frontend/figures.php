<html>
<head>
<title>TMPL: Topic Modeling in PL</title>
<?php

require_once('../../owa/owa_php.php');

$owa = new owa_php();
$owa->setSiteId('101db06411ab85d334726f4ec2344077');

$owa->setPageTitle('figures.php');
$owa->setPageType(isset($_FILES['userpdf']) ? 'upload' : 'view');
$owa->trackPageView();

?>
</head>
<body>
<center>
  <h1>TMPL: Topic Modeling in PL</h1>
  <h2>Tracking the flow of ideas through the programming languages literature</h2>
  <h3>
    <a href="http://www.cs.princeton.edu/~mg19/">Michael Greenberg</a>,
    <a href="http://www.cs.tufts.edu/~kfisher/Kathleen_Fisher/Home.html">Kathleen Fisher</a>, and
    <a href="http://www.cs.princeton.edu/~dpw/">David Walker</a>
  </h3>
</center>

<p>Check out our <a href="http://snapl.org/2015/">SNAPL</a> paper,
titled <a href="http://www.cs.princeton.edu/~mg19/papers/snapl2015.pdf">Tracking
the flow of ideas through the programming languages
literature</a>. Here we offer larger-scale PDFs of some of the figures
from our paper.</p>

<a href="figs/topics_all4.pdf"><img src="figs/topics_all4.png" /></a>
<p>Graphs of LOESS fits of topic proportions for each of the k=20
topics learned from abstracts from ICFP, OOPSLA, PLDI, and POPL.</p>

<a href="figs/topics_pldi_popl.pdf"><img src="figs/topics_pldi_popl.png" /></a>
<p>Graphs of LOESS fits of topic proportions for each of the k=20
topics learned from the full text documents from PLDI and POPL.</p>

<a href="figs/cite_with_random.pdf"><img src="figs/cite_with_random.png" /></a>
<p>Graphs comparing the Euclidean distance between four papers'
citations and the same number of randomly selected papers. CDRS
is <a href="http://dl.acm.org/citation.cfm?id=2254114">Concurrent data
representation synthesis</a>, PCC
is <a href="http://dl.acm.org/citation.cfm?id=263712">Proof-carrying
code</a>, SEMC
is <a href="http://dl.acm.org/citation.cfm?id=2676726.2676967">Space-efficient
manifest contracts</a>, and TAL
is <a href="http://dl.acm.org/citation.cfm?id=268954">From system F to
typed assembly language</a>.</p>

<a href="figs/cite_with_random_kl.pdf"><img src="figs/cite_with_random_kl.png" /></a>
<p>This graph is for the same data as the previous one, but
using <a href="http://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence">symmetrized
Kullback&ndash;Leibler divergence</a> as the distance metric instead
of Euclidean distance. Symmetrized KL divergence even more
dramatically separates related and unrelated work. The related work
search has been updated to use this metric, instead of Euclidean
distance.</p>

<a href="figs/abs_vs_fulltext_lda20_by_topic.pdf">
  <img src="figs/abs_vs_fulltext_lda20_by_topic.png" />
</a>
<p>Scatterplots indicating the overlap between the top 50 papers in
k=20 topics learned over abstracts and full text for PLDI and
POPL.</p>

</body>
</html>
