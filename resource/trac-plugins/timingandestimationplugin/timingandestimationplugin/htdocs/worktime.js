function moveFocus(e){
    id = e.target.id;
    ele = $("input[id^='hours_']");
    current_pos = -1;
    ele.each(function(i){
        if($(this).attr('id')==id){
            current_pos = i;
        }
    });
    if(current_pos==-1)return;
    if(navigator.appName.charAt(0)=="N")
        kc=e.which;
    if(navigator.appName.charAt(0)=="M")
        kc=event.keyCode;
    // up
    if(kc==38) {
          if(current_pos-1>=0){
              f = ele.get(current_pos-1);
              f.focus();
          }
    }
    // down
    if(kc==40) {
          if(current_pos+1<ele.length){
              f = ele.get(current_pos+1);
              f.focus();
          }
     }
}
document.onkeydown=moveFocus
