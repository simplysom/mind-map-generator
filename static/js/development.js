$(document).ready(function(){
    var sliders = ["#threshhold", "#maxConnections"];
    for (var i in sliders){
        var sldr = $(sliders[i]);
        sldr.next().html(sldr.val());
    }
    for (var i in sliders){
        var sldr = $(sliders[i]);
        sldr.on('input', function(){
            $(this).next().html($(this).val());
        });
    }

});

function changeParameters(){
  close_popup();
  var sliders = ["#threshhold", "#maxConnections"];
  var params = [];
  for (var i in sliders){
      var sldr = $(sliders[i]);
      params.push(sldr.val());
  }
  var url_string = '/juggad?&threshhold_value='+params[0]+
                   '&max_connections_value='+params[1]
  ReLoadFile(encodeURI(url_string));
}

function ReLoadFile(url_string) {

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {

            jsontext = this.response.split('|split|')[0];
            orignalText = this.response.split('|split|')[1];
            responseData=JSON.parse(jsontext);
            cy.elements().remove();
            load_graph();
        };
    }
        xhttp.open("GET", url_string, true);
        // xhttp.open("GET", "static/js/new_tree.json", true);
        xhttp.send();
}

function reset(){
    var sliders = ["#threshhold", "#maxConnections"];
    var default_values = [0.5, 5];
    for (var i in sliders){
        var sldr = $(sliders[i]);
        sldr.val(default_values[i]);
    }
    for (var i in sliders){
        var sldr = $(sliders[i]);
        sldr.next().html(sldr.val());
    }
    for (var i in sliders){
        var sldr = $(sliders[i]);
        sldr.on('input', function(){
            $(this).next().html($(this).val());
        });
    }
    changeParameters();
    load_graph();
}


function get_wiki_text(title){

  // Maintians record for previously called wiki for various nodes to avoid repeated calls
  if (define_record[title] == undefined){
    var url_string = '/wiki_text';
    $.ajax({
        type: "GET",
        url: url_string,
        data: {
          title: encodeURI(title)
        },
        success: function(data) {
            define_record[title] = data
            document.getElementById("meaning").innerHTML= data;
            return;
        }
    });
    return;
  } else {
    document.getElementById("meaning").innerHTML= define_record[title];
  }
}

function close_popup(){
  $('#pop-up').css("display", "none");
}

function html_format(text, title){
  var a = text.indexOf(title);
  if (a == -1){
    return "<li class='instance-para'>"+text+"</li>";
  }
  var b = a + title.length;
  return  "<li class='instance-para'>"
          + text.substring(0, a)
          + "<span>" + title + "</span>"
          + text.substring(b, text.length)
          + "</li>";
}

function get_origin_texts(ele){
  var i_s = ele.target.data().i;
  var j_s = ele.target.data().j;
  var return_string = "<ul>";
  var w_s = ele.target.data().word_instance;

  for(var i=0; i<i_s.length && i<j_s.length; i++){
    var sub_str = originalText.substring(i_s[i], j_s[i]);
    return_string += html_format(sub_str, w_s[i]);
  }

  return_string += "</ul>";

  return return_string;
}

function show_full_graph(){
  cy.elements().style("visibility","visible")
  setLayout("cose-bilkent",cy)
}
