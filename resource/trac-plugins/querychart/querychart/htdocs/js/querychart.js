$(function(){

$(".querychart").each(function(){
var idstr = this.id.split("_")[1];
var opt_upper = $("#querychartopt_"+idstr+" .upper").text().toLowerCase();
var opt_per = $("#querychartopt_"+idstr+" .per").text().toLowerCase();
var tzoffset = (new Date()).getTimezoneOffset()*60*1000;

var datas = [];
var labels = [];
var a, b, c, pre_c;
var i = 0;
$("#querycharttable_"+idstr+" tbody tr td").each(function(){
  switch (i ++ % 3){
  case 0:
    a = $(this).text(); break;
  case 1:
    b = new Date($(this).text()).getTime()-tzoffset; break;
  default:
    c = $(this).text();
    if (typeof datas[a] == "undefined"){
      datas[a] = [];
      labels.push(a);
    }
    
    if (opt_per != "free" || datas[a].length == 0 || c != pre_c){
      datas[a].push([b, c]);
      pre_c = c;
    }
  }
});
var vals = [];
var la;
i = labels.length;
while (i -- > 0){
  la = labels[i];
  vals[i] = { label: la, data: datas[la] };
}

var posit = opt_upper == "true" ? "se" : "ne";
var x_minTickSize = opt_per == "week" ? [7,"day"] : [1,"day"];

function showTooltip(x, y, contents){
  $('<div id="tooltip">'+contents+"</div>").css({
    position: "absolute",
    display: "none",
    top: (y + 5)+"px",
    left: (x + 5)+"px",
    border: "1px solid #fdd",
    padding: "2px",
    "background-color": "#fee",
    opacity: 0.80
  }).appendTo("body").fadeIn(200);
}


$.plot($("#placeholder_"+idstr), vals, {
  legend: { show: true, position: posit },
  lines: { show: true },
  points: { show: true },
  xaxis: { mode: "time", timeformat: "%y/%m/%d", minTickSize: x_minTickSize },
  yaxis: { min: 0, tickDecimals: 0,autoscaleMargin: 0.05 },
  grid: { hoverable: true, clickable: false }
});

var previousPoint = null;
$("#placeholder_"+idstr).bind("plothover", function (event, pos, item){

  if (item){
    if (previousPoint != item.datapoint){
      previousPoint = item.datapoint;
      
      $("#tooltip").remove();
      var x = item.datapoint[0],
          y = item.datapoint[1];
      var d = new Date(x);
      showTooltip(item.pageX, item.pageY,
                  item.series.label+"<br/>"
                   +d.getFullYear()+"/"+(d.getMonth()+1)+"/"+d.getDate()+" : "
                   +y);
    }
  }
  else {
    $("#tooltip").remove();
    previousPoint = null;
  }
});

});
});

