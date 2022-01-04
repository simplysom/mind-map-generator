function create_core_obj(container){
	var cy;
	if(container){
			cy=new cytoscape({
			container:document.getElementById(container_id)
		});
	}
	else{
		cy= new cytoscape();
	}
	return cy;
}

function LoadFile() {

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {

			jsontext = this.response.split('|split|')[0];
			originalText = this.response.split('|split|')[1];
		    responseData=JSON.parse(jsontext);
			load_graph();
		};
	}
		xhttp.open("GET", "/juggad", true);
		// xhttp.open("GET", "static/js/new_tree.json", true);
		xhttp.send();
}

function setLayout(lt, cy) {
	layout={
		name : lt,
		idealEdgeLength : 200,
		numIter:100000,
	};
	cy.layout(layout).run();
}


function addStyle(level_limit, ele) {
	cy.nodes().data("is_central",false);
	cy.collection().add(ele).data("is_central",true);
	cy.elements().style({
		"opacity" : '1',
		"visibility":"visible"
	});

	// old code
	central=cy.elements("node[?is_central]")[0];
	dijkstra=cy.elements("*").dijkstra({
		"root": "node[?is_central]"
	});

	cy.nodes().forEach( function(ele) {
		ele_level = this.distanceTo(ele);
		if (ele_level > level_limit){
			ele.style("visibility","hidden");
			ele.connectedEdges().style("visibility","hidden")
		}
	},dijkstra);

	setLayout("cose-bilkent", cy.elements(":visible"));
	// cy.fit(cy.elements(":visible"));
}

function load_graph(){
	jsonObject=responseData;
	cy.add(jsonObject['elements']);
	cy.style(style);
	// cy.nodes().ungrabify();
	cy.nodes().style({"visibility":"visible"});
	cy.edges().style({"visibility":"visible"});
	cy.nodes().on("select",function(ele) {

		//Pop-up related ops here eg. setting text, meaning etc...
		document.getElementById("title").innerHTML="<b>"+ele.target.data("title")+"</b>";

		if($('#pop-up input[type="checkbox"]')[0].checked == true){
			$('input[type="checkbox"]').trigger('click');
		};
		document.getElementById("subtree-btn").onclick=function(){
			addStyle(level_limit, ele.target);
		}

		document.getElementById("meaning").innerHTML=get_origin_texts(ele);

		$('input[type="checkbox"]').click(function(){
			if (this.checked == true){
				// To avoid repeated run of functions on all previously selected nodes
				if(ele.target.data('title') == last_selected){
					get_wiki_text(ele.target.data("title"));
				}
			}
			else {
				document.getElementById("meaning").innerHTML=get_origin_texts(ele);
			}
		});

		document.getElementById("pop-up").style.visibility = "hidden";
		document.getElementById("pop-up").style.display	= "grid";
		var box_position=ele.target.renderedPosition();
		var min_offset =50;
		var correction = -210;
		box_position.x+=(edge_length+min_offset)*cy.zoom();
		box_position.y-=(edge_length+min_offset)*cy.zoom();
		var maparea_rect	= document.getElementById("map-area").getBoundingClientRect();
		var popup_rect		= document.getElementById("pop-up").getBoundingClientRect();
		var box_left	=maparea_rect.left+box_position.x;
		var box_right	=box_left+popup_rect['width'];
		var box_top		=maparea_rect.top+box_position.y-popup_rect['height'];
		var box_bottom	=box_top;

		var popup_left=(box_right<=maparea_rect.right)?
															(box_left):
															(maparea_rect.width-popup_rect.width);
		var popup_top=(box_top>=maparea_rect.top)?
															(box_top):
															(maparea_rect.top);

		document.getElementById("pop-up").style.left		=	popup_left + correction + "px";
		document.getElementById("pop-up").style.top			= popup_top  + "px";
		document.getElementById("pop-up").style.visibility = "visible";

		// Keep record for last selected node
		last_selected = ele.target.data('title');

	});

	central=cy.elements("[?is_central]")[0]
	addStyle(level_limit, central);
	// setLayout("cose-bilkent", cy);

	// cy.cxtmenu( cxtmenuDefaults );
	// addStyle(level_limit, central);
}

function randomColor(ele){

	color = ['red', 'blue', 'green', 'gray', 'yellow']
	randomColor = color[Math.floor(Math.random()*color.length)]
	console.log(randomColor);
	ele.style("background-color", randomColor);
}

// function showText(ele){
//
// 	data = ele.data();
// 	origin_sent = originalText.substring(data.i,data.j);
// 	document.getElementById("meaning").innerHTML = origin_sent;
// }
