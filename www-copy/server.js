require('shelljs/global');
const exec = require('child_process').exec;
var express = require("express");
var multer = require("multer");
var fs = require("fs");
var app = express();
var server = require('http').createServer(app);
var upload = multer({dest: 'uploads/'});
var path = __dirname + '/web/';
var process = require('process');
var upload_dir = 'uploads';
var backend_dir = __dirname + '/backend/';

app.use(function (req,res,next) {
  console.log('/' + req.method);
  next();
});

app.use(express.static(path));

server.listen(3000,function(){
  console.log("Live at Port 3000");
});

app.get('/',function(req,res,next){
  res.sendFile(path + 'index.html');
  next();
});

app.get('/figures',function(req,res,next){
  res.sendFile(path + 'figures.html');
  next();
});

app.post('/', upload.single('userpdf'), function(req, res, next) {
  var mode = req.body.modes;
  var k = req.body.ks;
  var dfun = req.body.dist;
  var num = req.body.num || 20;
  var sub = req.body.submit;

  if (sub == "Visualize") {
    var newPath = path + "visuals/" + mode + "/" + k + "/";
    process.chdir(newPath);
    res.send(newPath + 'index.html');

    //res.redirect(307, newPath + 'index.html');
    //Cannot POST /Users/glorialiou/tmpl/www-copy/web/visuals/fulltext/20/index.html
  
    //res.sendFile(newPath + 'index.html');
    /*Error: Can't set headers after they are sent.
    at SendStream.headersAlreadySent (/Users/glorialiou/tmpl/www-copy/node_modules/express/node_modules/send/index.js:361:13)
    at SendStream.send (/Users/glorialiou/tmpl/www-copy/node_modules/express/node_modules/send/index.js:572:10)
    at onstat (/Users/glorialiou/tmpl/www-copy/node_modules/express/node_modules/send/index.js:677:10)
    at FSReqWrap.oncomplete (fs.js:123:15)*/

  } else if (!req.file) {
    res.send('No files were uploaded.');
  } else if (req.file.size > 41943040) {
    res.send('Your PDF was too big. Sorry!');
  } else {
    res.write("Processing " + req.file.originalname + "...\n");
    fs.mkdtemp(upload_dir + '/dir-', (err, folder) => {
      if (err) throw err;

      var fileName = folder + "/pdf";
      fs.rename(req.file.path, fileName, function(err) {
        process.chdir(backend_dir);
        process.env.PATH = '/n/fs/tmpl/.local/bin:/n/fs/tmpl/lda-c-dist:$PATH';
        process.env.PYTHONIOENCODING = 'utf8';
        exec("/usr/bin/python infer.py ../" + fileName + " " + mode + " "
          + k + " " + dfun + " " + num + " 2>&1", (error, stdout, stderr) => {
          if (error) {
            console.error(`exec error: ${error}`);
            return;
          }
          console.log(`stdout: ${stdout}`);
          console.log(`stderr: ${stderr}`);
          res.write(stdout);
          res.end();
        });
      });
    });
  }
  next();
});


