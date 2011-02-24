$(document).ready(function(){
  img_cache  = {};

  count = 0;
  e = $("span.author,td.担当者");
  if(e.length==0){
    return;
  }
  timer = setInterval(function(){
    username = $.trim(e[count].innerHTML);
    if((username!='somebody')&&(username!='anonymous')&&(username!='')){
      cache = img_cache[username];
      if(cache == undefined){ 
        $.ajax({
          url: avatar_request_path,
          data: {'id': count, 'username': username},
          dataType: 'json',
          type: 'GET',
          success: function(json){
            $(e[json['id']]).prepend('<img src="'+json['url']+'" style="max-width:40px; max-height: 40px; vertical-align:bottom;"/>');
            img_cache[json['username']] = json['url'];
          }
         });
       } else {
         $(e[count]).prepend('<img src="'+cache+'" style="max-width:40px; max-height: 40px; vertical-align:bottom;"/>');
       } 
    }
    count++;
    if(count == e.length){
       clearInterval(timer);
    }
  }, 20);
});

