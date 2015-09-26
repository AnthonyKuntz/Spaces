//images.js
module.exports = function() {
  
  //Ids and index are one and the same.
  var arr = [];
  
  function getElemsByIds(ids) {
    //console.log(ids);
    var ret1 = [];
    var ret2 = [];
    for(var i = 0; i < ids.length; i++) {
      ret1.push(ids[i]);
      ret2.push(arr[ids[i]]);
    }
    return [ret1, ret2];
  }

  function getElemsNotListed(ids) {
    console.log("Number of images: " + arr.length);
    var newIds = [];
    var aIdx = 0;
    var b;
    while(aIdx < arr.length) {
      b = false;
      for(var i = 0; i < ids.length; i++) {
        if(ids[i] === aIdx) {
          b = true;
          break;
        }
      }
      if(!b) {
        newIds.push(aIdx);
      }
      aIdx++;
    }

    return getElemsByIds(newIds);
  }

  function addElem(elem) {
    console.log("You added an element!");
    console.log(typeof elem);
    //console.log(elem.substring(0, 60));
    console.log(elem);
    arr.push(elem);
    return arr.length - 1; //returns the index/id
  }

  return {
    get: getElemsNotListed,
    add: addElem
  };
};
