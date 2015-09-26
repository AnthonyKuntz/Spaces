//app.js
var express = require('express');
var app = express();
var images = require('./images')();
//var http = require("http");

var announceIP = require('./announceIP');
var clientDir = __dirname.substring(0, __dirname.indexOf("\\server")) + "/client";

const PORT = 3000;

app.use(express.static("../client"));

app.get("/", function(req, res) {
  res.sendFile(clientDir + "/index.html");
});

var incoming = {}

app.get("/imagesPost", function(req, res) {

//   if(!req.query.images) {
//     res.sendStatus(400);
//     return;
//   }
  
  var user = req.query.user;
  var data = req.query.data;
  if(data === "start" || data === "\"start\"") {
    incoming[user] = [];
    res.send("1");
  } else if(data === "end" || data === "\"end\"") {
    var id = images.add(incoming[user]);
    res.send(JSON.stringify([id]));
  } else {
    //console.log(user + ": " + data);

    data = JSON.parse(data);
    for(i = 0; i < data.length; i++) {
      data[i][1] = 1919 - data[i][1];
      data[i][0] += 250;
      incoming[user].push(data[i]);
    }
    res.send("1");
  }

//   var indices = [];

//   for(var i = 0; i < imgs.length; i++) {
//     indices.push(images.add(imgs[i]));
//   }
  
  //console.log(req.query);
//   res.send(JSON.stringify(indices));
});

app.get("/imagesGet", function(req, res) {
  if(!req.query.images) {
    res.sendStatus(400);
    return;
  }

  var imgs = JSON.parse(req.query.images);
  //console.log(imgs);

  if(imgs.length === undefined) {
    res.sendStatus(400);
    return;
  }

  var ret = images.get(imgs);
  if(!ret) {
    res.sendStatus(500);
    return;
  }

  res.send(JSON.stringify(ret));
});

app.listen(PORT);
announceIP();
