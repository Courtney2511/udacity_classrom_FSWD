
function loadData() {

    var $body = $('body');
    var $wikiElem = $('#wikipedia-links');
    var $nytHeaderElem = $('#nytimes-header');
    var $nytElem = $('#nytimes-articles');
    var $greeting = $('#greeting');

    // clear out old data before new request
    $wikiElem.text("");
    $nytElem.text("");

    var streetStr = $('#street').val();
    var cityStr = $('#city').val();
    var address = streetStr + ', ' + cityStr;

    $greeting.text('So, you want to live at ' + address + '?');

    // load streetview
    var streetviewUrl = 'http://maps.googleapis.com/maps/api/streetview?size=600x400&location=' + address + '';
    $body.append('<img class="bgimg" src="' + streetviewUrl + '">');

    // load nytimes
    var url = "https://api.nytimes.com/svc/search/v2/articlesearch.json";
    url += '?' + $.param({
    'api-key': "31f60d1f2f40440f902ea4cf7a8d9326",
    'q': address,
    'sort': "newest"
    });

    $.getJSON(url, function(data){
      var articles = data.response.docs;
      console.log(articles);
      for (i=0; i < articles.length; i++ ) {
        var article = articles[i];
        $nytElem.append('<li class="article">'+'<a href="'+article.web_url+'">' +article.headline.main + '</a>'+'<p>'+article.snippet+'</p></li>');
      }
    }).fail(function(){
      console.log("it failed")
      $nytElem.append('<li>Articles could not be loaded</li>')
    });

    // load wikipedia-links
    var wikiUrl = 'http://en.wikipedia.org/w/api.php?action=opensearch&search=' + cityStr + '&format=json&callback=wikiCallback'

    // timer is a work around for error handling
    var wikiRequestTimeout = setTimeout(function(){
      $wikiElem.text("failed to load Wikipedia Resources");
    }, 8000);

    $.ajax({
      url: wikiUrl,
      dataType: "jsonp",
      success: function (response) {
        var articleList = response;
        console.log(articleList)
        for (i=0; i < articleList.length; i++) {
          var title = articleList[1][i];
          var url = articleList[3][i];
          console.log(title);
          console.log(url);
          $wikiElem.append('<li><a href="' + url + '">' + title + '</a></li>');
        };
        clearTimeout(wikiRequestTimeout)
      }
    });

    return false;
};

$('#form-container').submit(loadData);
