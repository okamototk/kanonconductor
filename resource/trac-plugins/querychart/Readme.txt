= Query Chart macro that draws in bug settling curve and Barndaunchart =
== Description ==
This is Wiki macro that counts the number of tickets, and draws in the bug settling curve and Barndaunchart.

Progress can be displayed good-looking by it not only puts on Wiki because it is Wiki macro but also displaying it with the time line and the report.

Moreover, the function to preserve in the custom field is bundled to this plug-in on the day when the status of the ticket changed. The day when the ticket closed can be made a graph by combining this with the graph.

== Requament ==
This plug-in is for Trac 0.11.

== Install ==
Please check it out from [http://coderepos.org/share/wiki CodeRepos] by using Subversion. In the command line client, as follows is done.

{{{
svn checkout http://svn.coderepos.org/share/platform/trac/plugins/querychart
}}}

Please move to /trunk and execute the following commands. :

{{{
$ python setup.py bdist_egg
}}}

The dist folder is made. Please copy *.egg file that is onto the plugins directory of TracEnv in that.

== Usage ==
=== Macro ===
The graph is displayed by describing the macro to wiki as follows.

{{{
[[QueryChart(args1,args2,...)]]
}}}

args:

 * query: Search condition of ticket. The following three kinds of can be described.
   * [http://trac.edgewall.org/wiki/TracQuery#QueryLanguage Query language] notation of TicketQuery macro:[[BR]]
     Write the condition without applying ? to the head.
     Refer to the [http://trac.edgewall.org/wiki/TracQuery#QueryLanguage Query language] for details.[[BR]]
     !query:status=new|assigned&version;^=1.0
   * Notation displayed in URL with custom query:[[BR]]
     Write conditions delimited by & applying ? (Without forgetting :) to the head as follows. It might be
     good to put the part of URL specifying the condition on the screen of custom query.[[BR]]
     !query:?status=new&status;=assigned&version;=^1.0
   * Omitte:[[BR]]
     It is possible to omit it only when putting it on the column the explanation of the report made from
     custom query (which displayed in address field of a browser). It becomes a search condition specified the
     omission on the screen. Please omit this item (query:...) when omitting it.
 * col: Targeted item. Please describe by col=xxx, col=yyy, and switching off the comma district when you
   specify the plural. The item name can specify both the field name (name of the field in Trac) and the label
   (displayed item name).
 * per:(=day,week,free) Unit of total. Default is week.
 * start: Day in left end of graph. If it is unspecification, it is the most past day of the ticket. yyyy/mm/dd form
 * end: Day on right edge in graph. If it is unspecification, it is the most recent day of the ticket. yyyy/mm/dd form
 * width: Width in graph. It specifies it by the unit of px. If it is unspecification, it is 536px.
 * height: Height of graph. It specifies it by the unit of px. If it is unspecification,    [[BR]]it is 300px.
 * upper: The improvement chart is written (bug settling curve etc.). Down chart when not specifying it.

ExampleF

{{{
[[QueryChart(query:?milestone=1.0ƒŠƒŠ[ƒX,col:due_close,col:due_assign,per:free,width:500,height:300)]]
}}}

=== Status Logger and Admin Page ===
The date can be preserved in the custom field automatically set when Ticket is changed by setting the priority level of status and the preserved custom field with Trac.ini. Moreover, the date can be set from the management screen in bulk.

It is necessary to decide the rule like "This day is assumed to be a completion day" in Trac because customizing the work flow is possible since Trac0.11 in addition to possible sending back the closing ticket. In this plug-in, "Generation order of status" is decided and the date is set according to it. The date is set in the custom field so that the generation order should not become low status from the one with high generation order ahead.

In the work flow of default, I think that it goes well roughly by the following priority levels. (By the way, because the date of the ticket enters the item named time even if the custom field is not prepared, it is unnecessary  )

(1)assigned (2)accepted (3)reopened (4)closed

For instance, it is assumed that close was suddenly done to 12/10 after assign is done to 12/01 as follows. In this case, the date of the same 12/10 as closed is set in accepted and reopened whose generation order is higher than closed. In addition, it is assumed that reopen was done to 12/20 afterwards. Closed whose generation order is lower than reopened is cleared to empty.

|| ||assigned||accepted||reopened||closed ||
||Assigned at 12/01||2008/12/01||-||-||- ||
||Afterwards, closed at 12/10||2008/12/01||2008/12/10||2008/12/10||2008/12/10 ||
||Afterwards, reopened at 12/20||2008/12/01||2008/12/10||2008/12/20||- ||
Next, please prepare the custom field to preserve the day of the generation of status. This need not prepare the sentence of all status. Please prepare only a necessary amount.

We will encourage to make it to the operation rule not input by the person so that this item may rewrite the value without permission in the plug-in.

Please set which generation order and custom field to preserve it to order of the QueryChart category of trac.ini. Status is delimited by the comma according to the generation order, the custom field preserved in addition is delimited by the colon after status, and it specifies it.

For instance, when last_assigned and the completion day are preserved in the custom field named last_closed, the day when assign was done is specified as follows by the generation order of the default work flow. By the way, if any custom field is not specified, the date is not preserved.

{{{
[querychart]order = assigned:last_assigned, accepted,reopened, closed:last_closed
}}}

Please set the date for all tickets pushing the reset button of ticket system -> QueryChart from the management screen after the plug-in is put and trac.ini is set. It is preserved in the custom field that the date automatically specified when the ticket is preserved after that. (The date doesn't enter by the automatic operation when the ticket is changed by the TicketDelete plug-in and the BatchModify plug-in. Please set the date from the management screen again. )

The date is set by the rule set to all tickets that the button is pushed. (The day when status actually changed according to the change tracking of the ticket is set. )

When change order of the QueryChart category of trac.ini, try to set the date pushing this button again.

== License ==
The license of this plug-in is new BSD license.

This plug-in uses the library named [http://code.google.com/p/flot/ Flot]. The license of Flot is MIT License.
