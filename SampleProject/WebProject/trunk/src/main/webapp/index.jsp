<%@page import="org.ultimania.sample.*" %>
<html>
<body>
<h2>Hello World!</h2>
<%
  SampleClass sc = new SampleClass();
   out.println(sc.getMessage());
%>
</body>
</html>
