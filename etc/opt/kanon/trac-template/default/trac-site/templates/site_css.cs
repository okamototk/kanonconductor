<?cs
##################################################################
# Site CSS - Place custom CSS, including overriding styles here.
?>

div.wikipage h1 {
  	font-size: 200%;
	border-width: 4px 0px 4px 0px;
	padding: 0px 4px 0px 4px;
        text-align: center;
	border-style: solid;
        border-color: #806080;
        background-color : #e0c0e0 ;
        filter: progid:DXImageTransform.Microsoft.gradient(startcolorstr=#ffc080c0, endcolorstr=#ffffffff, gradienttype=1,enabled=1);
        width: 100%;
}

div.wikipage h2 {
    	font-size: 160%;
        background-color : #e0c0e0 ;
        border-color : #806080;
  	border-style: solid;
	border-width: 0px 0px 0px 8px;
	padding: 0px 4px 0px 4px;
        filter: progid:DXImageTransform.Microsoft.gradient(startcolorstr=#ffc080c0, endcolorstr=#ffffffff, gradienttype=1,enabled=1);
        vertical-align: center;
        width: 100%;
}

div.wikipage h3 {
      	font-size: 120%;
        border-color: #848;
	border-style: double;
	border-width: 0px 0px 4px 0px;
	padding: 0px 4px 0px 4px;
}

div.wikipage h4 {
	border-style: solid;
        border-color: #848;
	border-width: 0px 0px 2px 0px;
	padding: 0px 4px 0px 4px;
}


pre.wiki {
        background-color : #eef ;
}


ul li {list-style-image:url(<?cs var:chrome.href ?>/site/css/icons/star.gif);}
ul li li {list-style-image:url(<?cs var:chrome.href ?>/site/css/icons/web.gif);}
ul li li li {list-style-image:url(<?cs var:chrome.href ?>/site/css/icons/record.gif);}

/* Navigation */
.wiki-toc ul {
  list-style:none;
  list-style-image:none;
}

.wiki-toc ul li {
  list-style: none;
  list-style-image:none;
}

