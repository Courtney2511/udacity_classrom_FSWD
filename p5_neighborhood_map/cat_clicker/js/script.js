

/** Model **/

var model = {
  currentCat: null,
  cats: [
          {
            "name": "Portia",
            "photo": "./imgs/cat.jpg",
            "clicks": 0
          },
          {
            "name": "Tabby",
            "photo": "./imgs/cat2.jpg",
            "clicks": 0
          },
          {
            "name": "Buddy",
            "photo": "./imgs/cat3.jpg",
            "clicks": 0
          },
          {
            "name": "Diablo",
            "photo": "./imgs/cat4.jpg",
            "clicks": 0
          },
          {
            "name": "Sandy",
            "photo": "./imgs/cat5.jpg",
            "clicks": 0
          }
        ]
  };

/** Octopus **/

var octopus = {

  // initializes the current cat and the list
  init: function() {
    model.currentCat = model.cats[0];
    catListView.init();
    catView.init();
  },

  // sets the current cat
  setCurrentCat: function(cat) {
    model.currentCat = cat
  },

  // gets current cat
  getCurrentCat: function() {
    return model.currentCat
  },

  // gets all cats
  getCats: function() {
    return model.cats
  },

  incrementCounter: function() {
    model.currentCat.clicks++;
    catView.render();
  }
}


/** Views **/

var catView = {
  init: function() {
    this.catElem = document.getElementById('cat-container')
    this.catNameElem = document.getElementById('cat')
    this.catImgElem = document.getElementById('cat-img')
    this.clickElem = document.getElementById('clicks-counter')

    this.catImgElem.addEventListener('click', function(){
      octopus.incrementCounter();
    });
    this.render()
  },

  render: function() {
    var currentCat = octopus.getCurrentCat();
    this.clickElem.textContent = currentCat.clicks;
    this.catNameElem.textContent = currentCat.name;
    this.catImgElem.src = currentCat.photo;
  }
}

var catListView = {
  init: function() {
    this.catListElem = document.getElementById('cat-list');
    this.render();
  },

  render: function() {
    var cats = octopus.getCats()
    for (i=0; i < cats.length; i++) {
      cat = cats[i];
      listItem = document.createElement('li');
      listItem.textContent = cat.name;
      listItem.addEventListener('click', (function(catCopy){
        return function() {
          octopus.setCurrentCat(catCopy);
          catView.render();
        };
      })(cat));
      this.catListElem.appendChild(listItem);
    }

  }
};

// initializes the page
octopus.init();
