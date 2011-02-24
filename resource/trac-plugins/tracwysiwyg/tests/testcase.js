addEvent(window, "load", function() {
    TracWysiwyg.tracPaths = { base: ".", search: "./search", stylesheets: [] };
    var options = TracWysiwyg.getOptions();
    var instance = new TracWysiwyg(document.getElementById("textarea"), options);
    var contentDocument = instance.contentDocument;

    var d = document;
    var wysiwygHtml = d.getElementById("wysiwyg-html");
    var showWysiwygHtml = d.getElementById("show-wysiwyg-html");
    setTimeout(function() {
        if (showWysiwygHtml.checked) {
            var body = contentDocument.body;
            var browserIE = body.attachEvent ? true : false;
            var elements = body.getElementsByTagName("br");
            var count = 0;
            var html = body.innerHTML.replace(/<[Bb][Rr] *[^>\/]*/g, function(value) {
                var element = elements[count++];
                var attributes = element.attributes;
                var length = attributes.length;
                if (length == 0)
                    return value;
                var texts = [ value ];
                for (var i = 0; i < length; i++) {
                    var attr = attributes[i];
                    if (!browserIE || !!element[attr.name]) {
                        texts.push(' ', attr.name, '="', attr.value, '"');
                    }
                }
                return texts.join("");
            });
            if (wysiwygHtml.value != html) {
                wysiwygHtml.value = html;
            }
        }
        setTimeout(arguments.callee, 500);
    }, 500);

    function generate(dom, wikitext, options, withoutDomToWikitext, withoutWikitextToFragment) {
        dom = dom.cloneNode(true);
        var anonymous = dom.ownerDocument.createElement("div");
        anonymous.appendChild(dom);

        if (!withoutWikitextToFragment) {
            var fragment = instance.wikitextToFragment(wikitext, contentDocument, options);
            var generated = contentDocument.createElement("div");
            generated.appendChild(fragment);
            var generatedHtml = generated.innerHTML;
            if (!generated.addEventListener || window.opera) {
                generatedHtml = generatedHtml.replace(/\n\r/g, "\uffff").replace(/\uffff\n?/g, "\n");
            }
            this.assertEqual(anonymous.innerHTML, generatedHtml, "wikitextToFragment");
        }
        if (!withoutDomToWikitext) {
            this.assertEqual(wikitext, instance.domToWikitext(anonymous, options), "domToWikitext");
        }
    }

    function generateFragment(dom, wikitext, options) {
        generate.call(this, dom, wikitext, options, true, false);
    }

    function generateWikitext(dom, wikitext, options) {
        generate.call(this, dom, wikitext, options, false, true);
    }

    function run() {
        var unit = new TracWysiwyg.TestUnit();
        var fragment = unit.fragment;
        var element = unit.element;
        var br = function() { return element("br") };
        var a = function(link, label) {
            var attrs = {
                href: "./search?q=" + encodeURIComponent(link),
                title: link, "tracwysiwyg-link": link, onclick: "return false;" };
            return element("a", attrs, label);
        };

        unit.add("treeWalk", function() {
            var list;
            function iterator(node) {
                var value;
                if (node) {
                    switch (node.nodeType) {
                    case 1: value = node.tagName.toLowerCase(); break;
                    case 3: value = "#text"; break;
                    }
                }
                else {
                    value = "(null)";
                }
                list.push(value);
            }

            function doTreeWalk(expected, dom) {
                list = [];
                instance.treeWalk(dom, iterator);
                this.assertEqual(expected, list.join(" "));

                list = [];
                instance._treeWalkEmulation(dom, iterator);
                this.assertEqual(expected, list.join(" "));
            }

            doTreeWalk.call(this, "p #text (null)", element("div", element("p", "paragraph")));
            doTreeWalk.call(this, "#text (null)", element("div", element("p", "paragraph")).firstChild);
            doTreeWalk.call(this, "(null)", element("div", element("p")).firstChild);

            var dom = element("div");
            dom.innerHTML = [
                '<h2 id="Tables">Tables</h2>',
                '<p>',
                'Simple tables can be created like this:',
                '</p>',
                '<pre class="wiki">||Cell 1||Cell 2||Cell 3||',
                '||Cell 4||Cell 5||Cell 6||',
                '</pre><p>',
                'Display:',
                '</p>',
                '<table class="wiki">',
                '<tbody><tr><td>Cell 1</td><td>Cell 2</td><td>Cell 3',
                '</td></tr><tr><td>Cell 4</td><td>Cell 5</td><td>Cell 6',
                '</td></tr></tbody></table>',
                '<p>',
                'Note that more complex tables can be created using',
                '<a class="wiki" href="/practice/wiki/WikiRestructuredText#BiggerReSTExample">reStructuredText</a>.',
                '</p>' ].join("");
            var expected = [
                'h2', '#text', 'p', '#text', 'pre', '#text', 'p', '#text',
                'table', 'tbody',
                'tr', 'td', '#text', 'td', '#text', 'td', '#text',
                'tr', 'td', '#text', 'td', '#text', 'td', '#text',
                'p', '#text', 'a', '#text', '#text',
                '(null)'].join(" ");
            doTreeWalk.call(this, expected, dom);
        });

        unit.add("isLastChildInBlockNode", function() {
            var dom = fragment(
                element("p", element("br")),
                element("p", "foobar", element("br"), "foobar"),
                element("p", element("b", "foobar", element("br"))),
                element("p", element("b", "foobar"), element("br")),
                element("br"));
            var count = 0;
            function assert(expected, node) {
                this.assertEqual(expected, instance.isLastChildInBlockNode(node), "#" + (count++));
            }
            assert.call(this, true,  dom.childNodes[0].childNodes[0]);
            assert.call(this, false, dom.childNodes[1].childNodes[0]);
            assert.call(this, false, dom.childNodes[1].childNodes[1]);
            assert.call(this, true,  dom.childNodes[1].childNodes[2]);
            assert.call(this, false, dom.childNodes[2].childNodes[0].childNodes[0]);
            assert.call(this, true,  dom.childNodes[2].childNodes[0].childNodes[1]);
            assert.call(this, false, dom.childNodes[3].childNodes[0].childNodes[0]);
            assert.call(this, true,  dom.childNodes[3].childNodes[1]);
            assert.call(this, true,  dom.childNodes[4]);
        });

        unit.add("code block", function() {
            var dom = fragment(
                element("p", element("tt", "abc")),
                element("pre", { "class": "wiki" }, "{{{code-block"));
            var wikitext = [
                "`abc`",
                "",
                "{{{",
                "{{{code-block",
                "}}}" ].join("\n");
            generate.call(this, dom, wikitext);
        });
        unit.add("code block nest", function() {
            var dom = fragment(
                element("pre", { "class": "wiki" }, "#!python\n= level 1\n{{{\n= level 2\n}}}\n= level 1"));
            var wikitext = [
                "{{{",
                "#!python",
                "= level 1",
                "{{{",
                "= level 2",
                "}}}",
                "= level 1",
                "}}}" ].join("\n");
            generate.call(this, dom, wikitext);
        });

        unit.add("paragraph", function() {
            var dom = fragment(
                element("p", "Paragraph continued..."),
                element("p", "Second paragraph continued..."));
            generateFragment.call(this, dom, [
                "Paragraph",
                "continued...",
                "",
                "Second paragraph",
                "continued...",
                "" ].join("\n"));
            generate.call(this, dom, [
                "Paragraph continued...",
                "",
                "Second paragraph continued..." ].join("\n"));
        });

        unit.add("hr", function() {
            var dom = fragment(
                element("p", "Paragraph"),
                element("hr"),
                element("ul",
                    element("li", "item 1"),
                    element("ol", element("li", "item 1.1"))),
                element("hr"));
            generateFragment.call(this, dom, [
                "Paragraph",
                "----",
                " * item 1",
                "   1. item 1.1",
                "----" ].join("\n"));
            generate.call(this, dom, [
                "Paragraph",
                "",
                "----",
                " * item 1",
                "   1. item 1.1",
                "",
                "----" ].join("\n"));
        });

        unit.add("bold italic", function() {
            var dom = element("p", element("b", element("i", "bold italic")));
            var wikitext = "'''''bold italic'''''";
            generate.call(this, dom, wikitext);
        });
        unit.add("bold", function() {
            var wikitext = [
                "The quick '''brown''' fox.",
                "",
                "The quick '''brown''' fox." ].join("\n");
            generateWikitext.call(this,
                fragment(
                    element("p", "The quick ", element("b", "brown"), " fox."),
                    element("p", "The quick ", element("strong", "brown"), " fox.")),
                wikitext);
            generateFragment.call(this,
                fragment(
                    element("p", "The quick ", element("b", "brown"), " fox."),
                    element("p", "The quick ", element("b", "brown"), " fox.")),
                wikitext);
        });
        unit.add("italic", function() {
            var wikitext = [
                "The quick ''brown'' fox.",
                "",
                "The quick ''brown'' fox." ].join("\n");
            generateWikitext.call(this,
                fragment(
                    element("p", "The quick ", element("i", "brown"), " fox."),
                    element("p", "The quick ", element("em", "brown"), " fox.")),
                wikitext);
            generateFragment.call(this,
                fragment(
                    element("p", "The quick ", element("i", "brown"), " fox."),
                    element("p", "The quick ", element("i", "brown"), " fox.")),
                wikitext);
        });
        unit.add("underline", function() {
            var dom = element("p", element("u", "underline"));
            var wikitext = "__underline__";
            generate.call(this, dom, wikitext);
        });
        unit.add("strike-through", function() {
            var dom = element("p", element("del", "strike-through"));
            var wikitext = "~~strike-through~~";
            generate.call(this, dom, wikitext);
        });
        unit.add("superscript", function() {
            var dom = element("p", element("sup", "superscript"));
            var wikitext = "^superscript^";
            generate.call(this, dom, wikitext);
        });
        unit.add("subscript", function() {
            var dom = element("p", element("sub", "subscript"));
            var wikitext = ",,subscript,,";
            generate.call(this, dom, wikitext);
        });
        unit.add("monospace", function() {
            var dom = element("p", element("tt", "monospace"),
                ", ", element("tt", "mono`s`pace"),
                ", ", element("tt", "mono{{{s}}}pace"));
            var wikitext = "`monospace`, {{{mono`s`pace}}}, `mono{{{s}}}pace`";
            generate.call(this, dom, wikitext);
        });
        unit.add("italic -> bold", function() {
            var dom = element("p",
                "normal",
                element("i", "italic"),
                element("b", "bold"),
                "normal");
            var wikitext = "normal''italic'''''bold'''normal";
            generate.call(this, dom, wikitext);
        });
        unit.add("bold -> italic", function() {
            var dom = element("p",
                "normal",
                element("b", "bold"),
                element("i", "italic"),
                "normal");
            var wikitext = "normal'''bold'''''italic''normal";
            generate.call(this, dom, wikitext);
        });
        unit.add("[ italic [ xyz ] bold ]", function() {
            var dom = element("p",
                "normal",
                element("i", "italic", element("b", "xyz")),
                element("b", "bold"),
                "normal");
            var wikitext = "normal''italic'''xyz''bold'''normal";
            generate.call(this, dom, wikitext);
        });
        unit.add("overlapped markups", function() {
            var dom = element("p",
                "normal",
                element("b", "bold",
                    element("i", "italic",
                        element("u", "underline",
                            element("del", "strike-through",
                                element("sup", "superscript",
                                    element("sub", "subscript"))))),
                    element("u", element("del", element("sup", element("sub", "i")))),
                    element("del", element("sup", element("sub", "u"))),
                    element("sup", element("sub", "strike")),
                    element("sub", "sup"),
                    "sub"),
                ".");
            var wikitext = "normal'''bold''italic__underline~~strike-through^superscript,,subscript''i__u~~strike^sup,,sub'''.";
            generateFragment.call(this, dom, wikitext);
        });

        unit.add("! bold italic", function() {
            var dom = element("p", element("b", element("i", "bold''''' italic")), ".");
            var wikitext = "'''''bold!''''' italic'''''.";
            generate.call(this, dom, wikitext);
        });
        unit.add("! bold", function() {
            var dom = element("p", element("b", "bold''' bold"), ".");
            var wikitext = "'''bold!''' bold'''.";
            generate.call(this, dom, wikitext);
        });
        unit.add("! italic", function() {
            var dom = element("p", element("i", "italic'' italic"), ".");
            var wikitext = "''italic!'' italic''.";
            generate.call(this, dom, wikitext);
        });
        unit.add("! underline", function() {
            var dom = element("p", element("u", "underline__ underline"), ".");
            var wikitext = "__underline!__ underline__.";
            generate.call(this, dom, wikitext);
        });
        unit.add("! strike-through", function() {
            var dom = element("p", element("del", "strike~~through"), ".");
            var wikitext = "~~strike!~~through~~.";
            generate.call(this, dom, wikitext);
        });
        unit.add("! superscript", function() {
            var dom = element("p", element("sup", "superscript^ superscript"), ".");
            var wikitext = "^superscript!^ superscript^.";
            generate.call(this, dom, wikitext);
        });
        unit.add("! subscript", function() {
            var dom = element("p", element("sub", "subscript,, subscript"), ".");
            var wikitext = ",,subscript!,, subscript,,.";
            generate.call(this, dom, wikitext);
        });
        unit.add("! monospace", function() {
            var dom = element("p", "{{{monospace}}} or `monospace`");
            var wikitext = "!{{{monospace}}} or !`monospace`";
            generate.call(this, dom, wikitext);
        });

        unit.add("!||, !=||", function() {
            var dom = fragment(
                element("p", "Paragraph"),
                element("table", { "class": "wiki" },
                    element("tbody",
                        element("tr", element("td", "foo||bar!||||==||foobar")))),
                element("p", "||||cell=||= =||||=cell|| Paragraph"));
            generateFragment.call(this, dom, [
                "Paragraph",
                "||foo!||bar!!||||=!=||foobar",
                "!||||cell!=||=",
                "!=||||=cell!||",
                "Paragraph" ].join("\n"));
            generate.call(this, dom, [
                "Paragraph",
                "",
                "|| foo!||bar!!||||=!=||foobar ||",
                "",
                "!||||cell!=||= !=||||=cell!|| Paragraph" ].join("\n"));
        });

        unit.add("#ticket", function() {
            var dom = element("p",
                element("a", "#1234", {
                    href: "./search?q=ticket%3A1234", title: "ticket:1234",
                    "tracwysiwyg-link": "ticket:1234", onclick: "return false;" }),
                " #2345 &#3456");
            var wikitext = "#1234 !#2345 &#3456";
            generate.call(this, dom, wikitext);
        });

        unit.add("{report}", function() {
            var dom = element("p",
                "{987}",
                element("a", "{123}", {
                    href: "./search?q=report%3A123", title: "report:123",
                    "tracwysiwyg-link": "report:123", onclick: "return false;" }));
            var wikitext = "!{987}{123}";
            generate.call(this, dom, wikitext);
        });

        unit.add("[changeset]", function() {
            var dom = element("p",
                element("a", "[123]", {
                    href: "./search?q=changeset%3A123", title: "changeset:123",
                    "tracwysiwyg-link": "changeset:123", onclick: "return false;" }),
                ", ",
                element("a", "r234", {
                    href: "./search?q=changeset%3A234", title: "changeset:234",
                    "tracwysiwyg-link": "changeset:234", onclick: "return false;" }),
                ", ",
                element("a", "[345/trunk]", {
                    href: "./search?q=changeset%3A345%2Ftrunk", title: "changeset:345/trunk",
                    "tracwysiwyg-link": "changeset:345/trunk", onclick: "return false;" }),
                ", [123], r234, [345/trunk], ar123");
            generate.call(this, dom, "[123], r234, [345/trunk], ![123], !r234, ![345/trunk], ar123");
        });

        unit.add("[log]", function() {
            var dom = element("p",
                "log - ",
                element("a", "r1:3", {
                    href: "./search?q=log%3A%401%3A3", title: "log:@1:3",
                    "tracwysiwyg-link": "log:@1:3", onclick: "return false;" }),
                ", r1:3, ",
                element("a", "[1:3]", {
                    href: "./search?q=log%3A%401%3A3", title: "log:@1:3",
                    "tracwysiwyg-link": "log:@1:3", onclick: "return false;" }),
                ", [1:3], ",
                element("a", "log:@1:3", {
                    href: "./search?q=log%3A%401%3A3", title: "log:@1:3",
                    "tracwysiwyg-link": "log:@1:3", onclick: "return false;" }),
                ", log:@1:3, ",
                element("a", "log:trunk@1:3", {
                    href: "./search?q=log%3Atrunk%401%3A3", title: "log:trunk@1:3",
                    "tracwysiwyg-link": "log:trunk@1:3", onclick: "return false;" }),
                ", log:trunk@1:3");
            generate.call(this, dom, "log - r1:3, !r1:3, [1:3], ![1:3], log:@1:3, !log:@1:3, log:trunk@1:3, !log:trunk@1:3");
        });

        unit.add("wiki:TracLinks", function() {
            var dom = element("p",
                element("a", "link:WikiName", {
                    href: "./search?q=link%3AWikiName", title: "link:WikiName",
                    "tracwysiwyg-link": "link:WikiName", onclick: "return false;" }),
                " ",
                element("a", 'link:"Foo Bar"', {
                    href: "./search?q=link%3A%22Foo%20Bar%22", title: 'link:"Foo Bar"',
                    "tracwysiwyg-link": 'link:"Foo Bar"', onclick: "return false;" }),
                " ",
                element("a", 'link:"Foo Bar#baz"', {
                    href: "./search?q=link%3A%22Foo%20Bar%23baz%22", title: 'link:"Foo Bar#baz"',
                    "tracwysiwyg-link": 'link:"Foo Bar#baz"', onclick: "return false;" }),
                " ",
                element("a", "link:'Foo Bar'", {
                    href: "./search?q=" + encodeURIComponent("link:'Foo Bar'"),
                    title: "link:'Foo Bar'", "tracwysiwyg-link": "link:'Foo Bar'",
                    onclick: "return false;" }),
                " ",
                element("a", "link:'Foo Bar#baz'", {
                    href: "./search?q=" + encodeURIComponent("link:'Foo Bar#baz'"),
                    title: "link:'Foo Bar#baz'", "tracwysiwyg-link": "link:'Foo Bar#baz'",
                    onclick: "return false;" }),
                " ",
                element("a", "svn+ssh://example.com/trunk", {
                    href: "./search?q=" + encodeURIComponent("svn+ssh://example.com/trunk"),
                    title: "svn+ssh://example.com/trunk", "tracwysiwyg-link": "svn+ssh://example.com/trunk",
                    onclick: "return false;" }),
                " ",
                element("a", "repository", {
                    href: "./search?q=" + encodeURIComponent("svn+ssh://example.com/trunk"),
                    title: "svn+ssh://example.com/trunk", "tracwysiwyg-link": "svn+ssh://example.com/trunk",
                    onclick: "return false;" }),
                " ",
                element("a", "rfc-2396.compatible://link", {
                    href: "./search?q=" + encodeURIComponent("rfc-2396.compatible://link"),
                    title: "rfc-2396.compatible://link", "tracwysiwyg-link": "rfc-2396.compatible://link",
                    onclick: "return false;" }),
                " ",
                element("a", "RFC 2396", {
                    href: "./search?q=" + encodeURIComponent("rfc-2396.compatible://link"),
                    title: "rfc-2396.compatible://link", "tracwysiwyg-link": "rfc-2396.compatible://link",
                    onclick: "return false;" }),
                " ",
                "21:09,",
                element("u", "underline"),
                ",abc123 !21:09,",
                element("u", "underline"),
                ",abc123",
                " ",
                element("a", "foo:bar", {
                    href: "./search?q=" + encodeURIComponent("foo:bar"),
                    title: "foo:bar", "tracwysiwyg-link": "foo:bar",
                    onclick: "return false;" }),
                " begin",
                element("a", "foo:bar", {
                    href: "./search?q=" + encodeURIComponent("foo:bar"),
                    title: "foo:bar", "tracwysiwyg-link": "foo:bar",
                    onclick: "return false;" }),
                " ",
                element("a", "foo:bar", {
                    href: "./search?q=" + encodeURIComponent("foo:bar"),
                    title: "foo:bar", "tracwysiwyg-link": "foo:bar",
                    onclick: "return false;" }),
                "end begin",
                element("a", "WikiStart", {
                    href: "./search?q=" + encodeURIComponent("wiki:WikiStart"),
                    title: "wiki:WikiStart", "tracwysiwyg-link": "wiki:WikiStart",
                    onclick: "return false;" }),
                "end link:'Foo Bar#baz'");
            generateFragment.call(this, dom, [
                "link:WikiName",
                'link:"Foo Bar" link:"Foo Bar#baz"',
                "link:'Foo Bar' link:'Foo Bar#baz'",
                "svn+ssh://example.com/trunk [svn+ssh://example.com/trunk repository]",
                "rfc-2396.compatible://link [rfc-2396.compatible://link RFC 2396]",
                "21:09,__underline__,abc123 !21:09,__underline__,abc123",
                "foo:bar begin[foo:bar foo:bar] [foo:bar foo:bar]end begin[wiki:WikiStart]end",
                "!link:'Foo Bar#baz'" ].join(" "));
            generate.call(this, dom, [
                "link:WikiName",
                'link:"Foo Bar" link:"Foo Bar#baz"',
                "link:'Foo Bar' link:'Foo Bar#baz'",
                "svn+ssh://example.com/trunk [svn+ssh://example.com/trunk repository]",
                "rfc-2396.compatible://link [rfc-2396.compatible://link RFC 2396]",
                "21:09,__underline__,abc123 !21:09,__underline__,abc123",
                "foo:bar begin[foo:bar foo:bar] [foo:bar foo:bar]end begin[wiki:WikiStart]end",
                "!link:'Foo Bar#baz'" ].join(" "));
        });

        unit.add("[wiki:TracLinks label]", function() {
            var dom = element("p",
                element("a", "WikiName", {
                    href: "./search?q=link%3AWikiName", title: "link:WikiName",
                    "tracwysiwyg-link": "link:WikiName", onclick: "return false;" }),
                " ",
                element("a", "wiki name", {
                    href: "./search?q=link%3AWikiName", title: "link:WikiName",
                    "tracwysiwyg-link": "link:WikiName", onclick: "return false;" }),
                " ",
                element("a", "wiki]name", {
                    href: "./search?q=wiki%3AWikiName", title: "wiki:WikiName",
                    "tracwysiwyg-link": "wiki:WikiName", onclick: "return false;" }),
                " ",
                element("a", "wiki name", {
                    href: "./search?q=wiki%3AWikiName", title: "wiki:WikiName",
                    "tracwysiwyg-link": "wiki:WikiName", onclick: "return false;" }),
                " ",
                element("a", "Foo Bar", {
                    href: "./search?q=link%3A%22Foo%20Bar%22", title: 'link:"Foo Bar"',
                    "tracwysiwyg-link": 'link:"Foo Bar"', onclick: "return false;" }),
                " ",
                element("a", "Foo Bar#baz", {
                    href: "./search?q=link%3A%22Foo%20Bar%23baz%22", title: 'link:"Foo Bar#baz"',
                    "tracwysiwyg-link": 'link:"Foo Bar#baz"', onclick: "return false;" }),
                " ",
                element("a", "bar foo", {
                    href: "./search?q=link%3A%22Foo%20Bar%22", title: 'link:"Foo Bar"',
                    "tracwysiwyg-link": 'link:"Foo Bar"', onclick: "return false;" }),
                " ",
                element("a", 'foo "foobar" bar', {
                    href: "./search?q=link%3A%22Foo%20Bar%23baz%22", title: 'link:"Foo Bar#baz"',
                    "tracwysiwyg-link": 'link:"Foo Bar#baz"', onclick: "return false;" }),
                " ",
                element("a", "Foo Bar", {
                    href: "./search?q=" + encodeURIComponent("link:'Foo Bar'"),
                    title: "link:'Foo Bar'", "tracwysiwyg-link": "link:'Foo Bar'",
                    onclick: "return false;" }),
                " ",
                element("a", "Foo Bar#baz", {
                    href: "./search?q=" + encodeURIComponent("link:'Foo Bar#baz'"),
                    title: "link:'Foo Bar#baz'", "tracwysiwyg-link": "link:'Foo Bar#baz'",
                    onclick: "return false;" }),
                " ",
                element("a", "foo bar", {
                    href: "./search?q=" + encodeURIComponent("link:'Foo Bar'"),
                    title: "link:'Foo Bar'", "tracwysiwyg-link": "link:'Foo Bar'",
                    onclick: "return false;" }),
                " ",
                element("a", "foo 'foobar' bar", {
                    href: "./search?q=" + encodeURIComponent("link:'Foo Bar#baz'"),
                    title: "link:'Foo Bar#baz'",
                    "tracwysiwyg-link": "link:'Foo Bar#baz'",
                    onclick: "return false;" }),
                " [link:'Foo Bar#baz'] [link:'Foo Bar#baz' label]");
            generateFragment.call(this, dom, [
                "[link:WikiName]",
                "[link:WikiName 'wiki name']",
                '[wiki:WikiName "wiki]name"]',
                "[WikiName 'wiki name']",
                '[link:"Foo Bar"] [link:"Foo Bar#baz"]',
                '[link:"Foo Bar" "bar foo"] [link:"Foo Bar#baz" foo "foobar" bar]',
                "[link:'Foo Bar'] [link:'Foo Bar#baz']",
                "[link:'Foo Bar' 'foo bar'] [link:'Foo Bar#baz' foo 'foobar' bar]",
                "![link:'Foo Bar#baz'] ![link:'Foo Bar#baz' label]" ].join(" "));
            generate.call(this, dom, [
                "[link:WikiName]",
                "[link:WikiName wiki name]",
                '[wiki:WikiName "wiki]name"]',
                "[wiki:WikiName wiki name]",
                '[link:"Foo Bar" Foo Bar] [link:"Foo Bar#baz" Foo Bar#baz]',
                '[link:"Foo Bar" bar foo] [link:"Foo Bar#baz" foo "foobar" bar]',
                "[link:'Foo Bar' Foo Bar] [link:'Foo Bar#baz' Foo Bar#baz]",
                "[link:'Foo Bar' foo bar] [link:'Foo Bar#baz' foo 'foobar' bar]",
                "![link:'Foo Bar#baz'] ![link:'Foo Bar#baz' label]" ].join(" "));
        });

        unit.add("[/relative label]", function() {
            var dom = element("p",
                element("a", "Trac", {
                    href: "../trac", title: "../trac", "tracwysiwyg-link": "../trac",
                    onclick: "return false;" }),
                " ",
                element("a", "here", {
                    href: "/newticket?component=tracwysiwygplugin",
                    title: "/newticket?component=tracwysiwygplugin",
                    "tracwysiwyg-link": "/newticket?component=tracwysiwygplugin",
                    onclick: "return false;" }),
                " ",
                element("a", "host", {
                    href: "//hostname", title: "//hostname", "tracwysiwyg-link": "//hostname",
                    onclick: "return false;" }),
                " ",
                element("a", "images", {
                    href: "//hostname/images", title: "//hostname/images",
                    "tracwysiwyg-link": "//hostname/images", onclick: "return false;" }),
                " ",
                element("a", "anchor", {
                    href: "#anchor", title: "#anchor", "tracwysiwyg-link": "#anchor",
                    onclick: "return false;" }));
            var wikitext = [
                "[../trac Trac]",
                "[/newticket?component=tracwysiwygplugin here]",
                "[//hostname host]",
                "[//hostname/images images]",
                "[#anchor anchor]" ].join(" ");
            generate.call(this, dom, wikitext);
        });

        unit.add("<wiki:bracket links>", function() {
            function a(link) {
                return element("a", link, {
                    href: "./search?q=" + encodeURIComponent(link),
                    title: link, "tracwysiwyg-link": link, onclick: "return false;" });
            }
            var dom = fragment(
                element("p", "<", a("link:1"), ">"),
                element("p", "Thing<", a("link:2 and (3)"), ">"),
                element("p", "<link:1>"),
                element("p", "Thing<link:2 and (3)>"));
            var wikitext = [
                "<link:1>",
                "",
                "Thing<link:2 and (3)>",
                "",
                "!<link:1>",
                "",
                "Thing!<link:2 and (3)>" ].join("\n");
            generate.call(this, dom, wikitext);
        });

        unit.add("[=#anchor]", function() {
            function a(link) {
                return element("a", link, {
                    href: "./search?q=" + encodeURIComponent(link),
                    title: link, "tracwysiwyg-link": link, onclick: "return false;" });
            }
            var dom = fragment(
                element("p",
                    "This is the ",
                    element("span", { "class": "wikianchor", id: "init" }),
                    " initialization routine: ..."),
                element("p",
                    "Look for ",
                    element("span", { "class": "wikianchor", id : "extra" },
                        element("i", "additional explanations")),
                    " here."),
                element("p",
                    "これは",
                    element("span", { "class": "wikianchor", id: "初期化" }),
                    "初期化ルーチン: ..."),
                element("p",
                    element("span", { "class": "wikianchor", id : "追加" }, element("i", "追加説明")),
                    "はここを見てください。"));
            var wikitext = [
                "This is the [=#init] initialization routine: ...",
                "",
                "Look for [=#extra ''additional explanations''] here.",
                "",
                "これは[=#初期化]初期化ルーチン: ...",
                "",
                "[=#追加 ''追加説明'']はここを見てください。" ].join("\n");
            generate.call(this, dom, wikitext);
        });

        unit.add("[[macro]]", function() {
            var dom = element("p",
                "Line break ", element("br"), " another line", element("br"),
                "last line [[bR]] ![[Br]] [[Macro]] ![[Macro]] [[Image?]] ![[Image?]] [[?]] ![[?]]");
            generateFragment.call(this, dom, "Line break [[BR]] another line[[br]]last line ![[bR]] !![[Br]] [[Macro]] ![[Macro]] [[Image?]] ![[Image?]] [[?]] ![[?]]");
            generate.call(this, dom, "Line break [[BR]] another line[[BR]]last line ![[bR]] !![[Br]] [[Macro]] ![[Macro]] [[Image?]] ![[Image?]] [[?]] ![[?]]");
        });

        unit.add("WikiPageName", function() {
            var dom = fragment(
                element("p",
                    a("wiki:CamelCase", "CamelCase"),
                    " CamelCase FooBarA FOo FoobarA OneÅngström Oneångström setTextColor"),
                element("p",
                    a("wiki:WikiStart", "WikiStart"),
                    " Wiki",
                    a("wiki:Start", "Start"),
                    " ",
                    a("wiki:Wiki", "Wiki"),
                    "Start Wiki",
                    a("wiki:Start", "Start"),
                    "Wiki"));
            generate.call(this, dom, [
                "CamelCase !CamelCase FooBarA FOo FoobarA OneÅngström Oneångström setTextColor",
                "",
                "WikiStart Wiki[wiki:Start] [wiki:Wiki]Start Wiki[wiki:Start]Wiki" ].join("\n"));
        });

        unit.add('["internal free link"]', function() {
            var dom = element("p",
                "link - ",
                element("a", "internal free link", {
                    href: "./search?q=" + encodeURIComponent('wiki:"internal free link"'),
                    title: 'wiki:"internal free link"', "tracwysiwyg-link": 'wiki:"internal free link"',
                    onclick: "return false;" }),
                ' - ["free link"]');
            generate.call(this, dom, 'link - [wiki:"internal free link" internal free link] - !["free link"]');
        });

        unit.add("traclink + underline", function() {
            var dom = element("p",
                element("u", a("ticket:123", "#123")), " ",
                a("ticket:123", element("u", "#123")), " ",
                element("u", a("report:123", "{123}")), " ",
                a("report:123", element("u", "{123}")), " ",
                element("u", a("changeset:123", "[123]")), " ",
                a("changeset:123", element("u", "[123]")), " ",
                element("u", a("changeset:123", "r123")), " ",
                a("changeset:123", element("u", "r123")), " ",
                element("u", a("log:@123:234", "[123:234]")), " ",
                a("log:@123:234", element("u", "[123:234]")), " ",
                element("u", a("wiki:WikiStart", "wiki:WikiStart")), " ",
                a("wiki:WikiStart", element("u", "wiki:WikiStart")), " ",
                element("u", a("wiki:WikiStart", "WikiStart")), " ",
                a("wiki:WikiStart", element("u", "WikiStart")));
            generateWikitext.call(this, dom, [
                '__#123__',
                '__#123__',
                '__{123}__',
                '__{123}__',
                '__[123]__',
                '__[123]__',
                '__[changeset:123 r123]__',
                '__[changeset:123 r123]__',
                '__[123:234]__',
                '__[123:234]__',
                '__[wiki:WikiStart wiki:WikiStart]__',
                '__[wiki:WikiStart wiki:WikiStart]__',
                '__[wiki:WikiStart]__',
                '__[wiki:WikiStart]__' ].join(" "));
        });

        unit.add("token + br", function() {
            var dom = fragment(
                element("p", "head ", a("http://localhost/", "http://localhost/"), element("br"), "tail"),
                element("p", "head http://localhost/", element("br"), "tail"),
                element("p", "head ", element("tt", "teletype"), element("br"), "tail"),
                element("p", "head ", a("wiki:TracLinks", "TracLinks"), element("br"), "tail"),
                element("p",
                    "head ", a("http://localhost/", "http://localhost/"), " ",
                    a("wiki:TracLinks", "wiki:TracLinks"),
                    element("br"),
                    "tail"),
                element("p", "head http://localhost/ wiki:TracLinks", element("br"), "tail"));
            generateWikitext.call(this, dom, [
                "head http://localhost/ [[BR]]tail",
                "",
                "head !http://localhost/ [[BR]]tail",
                "",
                "head `teletype`[[BR]]tail",
                "",
                "head TracLinks[[BR]]tail",
                "",
                "head http://localhost/ wiki:TracLinks [[BR]]tail",
                "",
                "head !http://localhost/ !wiki:TracLinks [[BR]]tail" ].join("\n"));
        });

        if (window.getSelection) {
            unit.add("block + br", function() {
                function br() { return element("br"); }
                var wikitext = [
                    "text, br",
                    "",
                    "text'', br[[BR]]''",
                    "",
                    "|| 1,1[[BR]] || || 1,3 ||",
                    "|| || 2,2[[BR]][[BR]] ||",
                    "",
                    " * list, br[[BR]]",
                    " * list, br",
                    " * ",
                    "",
                    "text, br[[BR]]" ].join("\n")
                generateWikitext.call(this,
                    fragment(
                        element("p", "text, br", br()),
                        element("p", "text", element("i", ", br", br()), br()),
                        element("table", { "class": "wiki" },
                            element("tbody",
                                element("tr",
                                    element("td", "1,1", br(), br()),
                                    element("td", br()),
                                    element("td", "1,3", br())),
                                element("tr",
                                    element("td", br()),
                                    element("td", "2,2", br(), br(), br())))),
                        element("ul",
                            element("li", "list, br", br(), br()),
                            element("li", "list, br", br()),
                            element("li")),
                        element("p", "text, br", br(), br())),
                    wikitext);
                generateFragment.call(this,
                    fragment(
                        element("p", "text, br"),
                        element("p", "text", element("i", ", br", br()), br()),
                        element("table", { "class": "wiki" },
                            element("tbody",
                                element("tr",
                                    element("td", "1,1", br(), br()),
                                    element("td", br()),
                                    element("td", "1,3")),
                                element("tr",
                                    element("td", br()),
                                    element("td", "2,2", br(), br(), br())))),
                        element("ul",
                            element("li", "list, br", br(), br()),
                            element("li", "list, br"),
                            element("li", br())),
                        element("p", "text, br", br(), br())),
                    wikitext);
            });
        }
        else {
            unit.add("block + br", function() {
                function br() { return element("br"); }
                var wikitext = [
                    "text, br",
                    "",
                    "text'', br[[BR]]''",
                    "",
                    "|| 1,1[[BR]] || || 1,3 ||",
                    "|| || 2,2[[BR]][[BR]] ||",
                    "",
                    " * list, br[[BR]]",
                    " * list, br",
                    " * ",
                    "",
                    "text, br[[BR]]" ].join("\n")
                generate.call(this,
                    fragment(
                        element("p", "text, br"),
                        element("p", "text", element("i", ", br", br())),
                        element("table", { "class": "wiki" },
                            element("tbody",
                                element("tr",
                                    element("td", "1,1", br()),
                                    element("td"),
                                    element("td", "1,3")),
                                element("tr",
                                    element("td"),
                                    element("td", "2,2", br(), br())))),
                        element("ul",
                            element("li", "list, br", br()),
                            element("li", "list, br"),
                            element("li")),
                        element("p", "text, br", br())),
                    wikitext);
            });
        }

        unit.add("citation", function() {
            var dom = fragment(
                element("blockquote", { "class": "citation" },
                    element("p", "This is the quoted text continued"),
                    element("blockquote", { "class": "citation" },
                        element("p", "a nested quote"),
                        element("blockquote", { "class": "citation" },
                            element("p", "a nested-nested quote")))),
                element("p", "A comment on the above"),
                element("blockquote", { "class": "citation" },
                    element("blockquote", { "class": "citation" },
                        element("p", "start 2nd level")),
                    element("p", "first level")));
            generateFragment.call(this, dom, [
                "> This is the quoted text",
                "> continued",
                "> > a nested quote",
                "> > > a nested-nested quote",
                "A comment on the above",
                "> > start 2nd level",
                ">first level" ].join("\n"));
            generate.call(this, dom, [
                "> This is the quoted text continued",
                "> > a nested quote",
                "> > > a nested-nested quote",
                "",
                "A comment on the above",
                "",
                "> > start 2nd level",
                "> first level" ].join("\n"));
        });

        unit.add("header", function() {
            var dom = fragment(
                element("h1", "Heading 1"),
                element("h2", { id: "anchor-2" }, "Heading 2"),
                element("h3", element("u", "Heading"), " ", element("i", "3")),
                element("h4", { id: "アンカー-4" },
                    "Heading 4 with ",
                    element("a", "link", {
                        href: "./search?q=" + encodeURIComponent('wiki:WikiStart'),
                        title: 'wiki:WikiStart', "tracwysiwyg-link": 'wiki:WikiStart',
                        onclick: "return false;" })),
                element("h5", "Heading 5"),
                element("h6", { id: "anchor-6" }, "Heading 6"));
            generate.call(this, dom, [
                "= Heading 1 =",
                "== Heading 2 == #anchor-2",
                "=== __Heading__ ''3'' ===",
                "==== Heading 4 with [wiki:WikiStart link] ==== #アンカー-4",
                "===== Heading 5 =====",
                "====== Heading 6 ====== #anchor-6" ].join("\n"));
        });

        unit.add("header 2", function() {
            var dom = fragment(
                element("h1", "Heading 1"),
                element("h2", { id: "anchor-2" }, "Heading 2"),
                element("h3", element("u", "Heading"), " ", element("i", "3")),
                element("h4", { id: "アンカー-4" },
                    "Heading 4 with ",
                    element("a", "link", {
                        href: "./search?q=" + encodeURIComponent('wiki:WikiStart'),
                        title: 'wiki:WikiStart', "tracwysiwyg-link": 'wiki:WikiStart',
                        onclick: "return false;" })),
                element("h5", "Heading 5"),
                element("h6", { id: "anchor-6" }, "Heading 6"));
            generateFragment.call(this, dom, [
                "= Heading 1  ",
                "== Heading 2    #anchor-2",
                "=== __Heading__ ''3''    ",
                "==== Heading 4 with [wiki:WikiStart link]      #アンカー-4",
                "===== Heading 5      ",
                "====== Heading 6        #anchor-6" ].join("\n"));
        });

        unit.add("list", function() {
            var dom = fragment(
                element("p", "Paragraph"),
                element("ul",
                    element("li", "foo bar boo baz"),
                    element("ul", element("li", "Subitem Subitem line 2")),
                    element("li", "item 2 item 2 line 2")),
                element("p", "Paragraph"));
            generateFragment.call(this, dom, [
                "Paragraph",
                " * foo bar",
                "   boo baz",
                "   * Subitem",
                "     Subitem line 2",
                " * item 2",
                "   item 2 line 2",
                "Paragraph" ].join("\n"));
            generate.call(this, dom, [
                "Paragraph",
                "",
                " * foo bar boo baz",
                "   * Subitem Subitem line 2",
                " * item 2 item 2 line 2",
                "",
                "Paragraph" ].join("\n"));
        });

        unit.add("list 2", function() {
            var dom = fragment(
                element("ul",
                    element("li", "foo bar boo baz"),
                    element("ul",
                        element("li", "Subitem 1"),
                        element("ul",
                            element("li", "nested item 1"),
                            element("li", "nested item 2 nested item 2 continued")),
                        element("li", "Subitem 2 subitem 2 continued"),
                        element("li", "Subitem 3 subitem 3 continued")),
                    element("li", "item 2 item 2 line 2")),
                element("p", "Paragraph"));
            generateFragment.call(this, dom, [
                "    * foo bar",
                "      boo baz",
                "           * Subitem 1",
                "             - nested item 1",
                "             - nested item 2",
                "             nested item 2 continued",
                "            * Subitem 2",
                "             subitem 2 continued",
                "            * Subitem 3",
                "            subitem 3 continued",
                "    * item 2",
                "     item 2 line 2",
                "Paragraph" ].join("\n"));
            generate.call(this, dom, [
                " * foo bar boo baz",
                "   * Subitem 1",
                "     * nested item 1",
                "     * nested item 2 nested item 2 continued",
                "   * Subitem 2 subitem 2 continued",
                "   * Subitem 3 subitem 3 continued",
                " * item 2 item 2 line 2",
                "",
                "Paragraph" ].join("\n"));
        });

        unit.add("ordered list", function() {
            var dom = fragment(
                element("p", "Paragraph"),
                element("ol",
                    element("li", "item 1"),
                    element("ol", { "class": "arabiczero" },
                        element("li", "item 1.1"),
                        element("li", "item 1.2"),
                        element("ol", { "class": "loweralpha" },
                            element("li", "item 1.2.a"),
                            element("li", "item 1.2.b")),
                        element("li", "item 1.3"),
                        element("ol", { "class": "loweralpha" },
                            element("li", "item 1.3.a"),
                            element("li", "item 1.3.b")),
                        element("li", "item 1.4"),
                        element("ol", { "class": "upperalpha" },
                            element("li", "item 1.4.A"),
                            element("li", "item 1.4.B"),
                            element("li", "item 1.4.C")),
                        element("li", "item 1.5"),
                        element("ol", { "class": "upperalpha" },
                            element("li", "item 1.5.A")),
                        element("li", "item 1.6"),
                        element("ol", { "class": "lowerroman" },
                            element("li", "item 1.6.i"),
                            element("li", "item 1.6.ii")),
                        element("li", "item 1.7"),
                        element("ol", { "class": "upperroman" },
                            element("li", "item 1.7.I"),
                            element("li", "item 1.7.II")))),
                element("p", "Paragraph"));
            generateFragment.call(this, dom, [
                "Paragraph",
                " 1. item 1",
                "   0. item 1.1",
                "   2. item 1.2",
                "     a. item 1.2.a",
                "     z. item 1.2.b",
                "   a. item 1.3",
                "     b. item 1.3.a",
                "     y. item 1.3.b",
                "   Z. item 1.4",
                "     A. item 1.4.A",
                "     z. item 1.4.B",
                "     z. item 1.4.C",
                "   ii. item 1.5",
                "     C. item 1.5.A",
                "   XVI. item 1.6",
                "     i. item 1.6.i",
                "     x. item 1.6.ii",
                "   0. item 1.7",
                "     I. item 1.7.I",
                "     III. item 1.7.II",
                "Paragraph" ].join("\n"));
            generate.call(this, dom, [
                "Paragraph",
                "",
                " 1. item 1",
                "   0. item 1.1",
                "   0. item 1.2",
                "     a. item 1.2.a",
                "     a. item 1.2.b",
                "   0. item 1.3",
                "     a. item 1.3.a",
                "     a. item 1.3.b",
                "   0. item 1.4",
                "     A. item 1.4.A",
                "     A. item 1.4.B",
                "     A. item 1.4.C",
                "   0. item 1.5",
                "     A. item 1.5.A",
                "   0. item 1.6",
                "     i. item 1.6.i",
                "     i. item 1.6.ii",
                "   0. item 1.7",
                "     I. item 1.7.I",
                "     I. item 1.7.II",
                "",
                "Paragraph" ].join("\n"));
        });

        unit.add("list + ordered list", function() {
            var dom = fragment(
                element("ul",
                    element("li", "Item 1"),
                    element("ul", element("li", "Item 1.1")),
                    element("li", "Item 2")),
                element("ol",
                    element("li", "Item 1"),
                    element("ol", { "class": "loweralpha" },
                        element("li", "Item 1.a"),
                        element("li", "Item 1.b"),
                        element("ol", { "class": "lowerroman" },
                            element("li", "Item 1.b.i"),
                            element("li", "Item 1.b.ii"))),
                    element("li", "Item 2")),
                element("p", "And numbered lists can also be given an explicit number:"),
                element("ol", { start: 3 }, element("li", "Item 3")));
            generateFragment.call(this, dom, [
                " * Item 1",
                "   * Item 1.1",
                " * Item 2",
                " 1. Item 1",
                "   a. Item 1.a",
                "   a. Item 1.b",
                "      i. Item 1.b.i",
                "      i. Item 1.b.ii",
                " 1. Item 2",
                "And numbered lists can also be given an explicit number:",
                " 3. Item 3" ].join("\n"));
            generate.call(this, dom, [
                " * Item 1",
                "   * Item 1.1",
                " * Item 2",
                "",
                " 1. Item 1",
                "   a. Item 1.a",
                "   a. Item 1.b",
                "     i. Item 1.b.i",
                "     i. Item 1.b.ii",
                " 1. Item 2",
                "",
                "And numbered lists can also be given an explicit number:",
                "",
                " 3. Item 3" ].join("\n"));
        });

        unit.add("list at beginning of line", function() {
            var dom = fragment(
                element("ul",
                    element("li", "item 1"),
                    element("li", "item 2"),
                    element("ul", element("li", "sub 2.1"), element("li", "sub 2.2"))),
                element("ol", { "class": "loweralpha" },
                    element("li", "item A"), element("li", "item B")),
                element("p", "Paragraph"));
            generateFragment.call(this, dom, [
                "- item 1",
                "- item 2",
                "  - sub 2.1",
                "  - sub 2.2",
                "a. item A",
                "b. item B",
                "Paragraph" ].join("\n"));
            generate.call(this, dom, [
                " * item 1",
                " * item 2",
                "   * sub 2.1",
                "   * sub 2.2",
                "",
                " a. item A",
                " a. item B",
                "",
                "Paragraph" ].join("\n"));
        });

        unit.add("list + code block", function() {
            var dom = fragment(
                element("p", "Paragraph"),
                element("ul",
                    element("li",
                        "item 1",
                        element("pre", { "class": "wiki" }, "code")),
                    element("ul",
                        element("li",
                            "item 1.1",
                            element("pre", { "class": "wiki" }, "code"),
                            "cont.",
                            element("pre", { "class": "wiki" }, "code"))),
                    element("li",
                        "item 2",
                        element("pre", { "class": "wiki" }, "code"))),
                element("ol", element("li", "item 1")));
            generateFragment.call(this, dom, [
                "Paragraph",
                " * item 1",
                "{{{",
                "code",
                "}}}",
                "   * item 1.1",
                "{{{",
                "code",
                "}}}",
                "     cont.",
                "{{{",
                "code",
                "}}}",
                " * item 2",
                "{{{",
                "code",
                "}}}",
                " 1. item 1" ].join("\n"));
            generate.call(this, dom, [
                "Paragraph",
                "",
                " * item 1",
                "{{{",
                "code",
                "}}}",
                "   * item 1.1",
                "{{{",
                "code",
                "}}}",
                "     cont.",
                "{{{",
                "code",
                "}}}",
                " * item 2",
                "{{{",
                "code",
                "}}}",
                "",
                " 1. item 1" ].join("\n"));
        });

        unit.add("list + citation", function() {
            var dom = fragment(
                element('ol', element('li', 'item 1')),
                element('blockquote', { 'class': 'citation' }, element("p", "citation 1")),
                element('ul',
                    element('li', 'item 2'),
                    element("ol",
                        element('li', 'item 2.1'),
                        element('li', 'item 2.2'))),
                element('blockquote', { 'class': 'citation' }, element("p", "citation 2 citation 3")),
                element('ol', element('li', 'item 3')));
            generateFragment.call(this, dom, [
                ' 1. item 1',
                '> citation 1',
                ' * item 2',
                '   1. item 2.1',
                '   1. item 2.2',
                '> citation 2',
                '> citation 3',
                ' 1. item 3' ].join("\n"));
            generateWikitext.call(this, dom, [
                ' 1. item 1',
                '',
                '> citation 1',
                '',
                ' * item 2',
                '   1. item 2.1',
                '   1. item 2.2',
                '',
                '> citation 2 citation 3',
                '',
                ' 1. item 3' ].join("\n"));
        });

        unit.add("definition", function() {
            var dom = element("dl",
                element("dt", "python"),
                element("dd", "www.python.org :: cont."),
                element("dt", element("b", "trac")),
                element("dd",
                    element("b", "trac"), ".edgewall.org cont.",
                    " ", element("tt", "trac-hacks::"), " trac-hacks.org"));
            generateFragment.call(this, dom, [
                " python:: www.python.org :: cont.",
                " '''trac''':: '''trac'''.edgewall.org",
                "   cont.",
                " `trac-hacks::` trac-hacks.org" ].join("\n"));
            generate.call(this, dom, [
                " python:: www.python.org :: cont.",
                " '''trac''':: '''trac'''.edgewall.org cont. `trac-hacks::` trac-hacks.org" ].join("\n"));
        });

        unit.add("blockquote", function() {
            var dom = fragment(
                element("p", "Paragraph"),
                element("blockquote",
                    element("p", "blockquote 1 cont. 1"),
                    element("blockquote",
                        element("p", "blockquote 1.1"),
                        element("blockquote", element("p", "blockquote 1.1.1 cont. 1.1.1")),
                        element("p", "blockquote 1.2")),
                    element("p", "blockquote 2")),
                element("p", "Paragraph"));
            generateFragment.call(this, dom, [
                "Paragraph",
                "  blockquote 1",
                "  cont. 1",
                "    blockquote 1.1",
                "      blockquote 1.1.1",
                "      cont. 1.1.1",
                "     blockquote 1.2",
                "    blockquote 2",
                "Paragraph" ].join("\n"));
            generate.call(this, dom, [
                "Paragraph",
                "",
                "  blockquote 1 cont. 1",
                "    blockquote 1.1",
                "      blockquote 1.1.1 cont. 1.1.1",
                "    blockquote 1.2",
                "  blockquote 2",
                "",
                "Paragraph" ].join("\n"));
        });

        unit.add("table", function() {
            var dom = fragment(
                element("p", "Paragraph"),
                element("table", { "class": "wiki" },
                    element("tbody",
                        element("tr", element("td", "1.1"), element("td", "1.2")),
                        element("tr", element("td", "2.1")),
                        element("tr",
                            element("td", "3.1"),
                            element("td", element("u", "3.2")),
                            element("td", element("tt", "3"), " ", element("tt", "-"))))),
                element("p", "Paragraph"));
            generateFragment.call(this, dom, [
                "Paragraph",
                "||1.1||1.2||",
                "||2.1",
                "||3.1||__3.2__||`3` `-`",
                "Paragraph" ].join("\n"));
            generate.call(this, dom, [
                "Paragraph",
                "",
                "|| 1.1 || 1.2 ||",
                "|| 2.1 ||",
                "|| 3.1 || __3.2__ || `3` `-` ||",
                "",
                "Paragraph" ].join("\n"));
        });

        unit.add("colspan", function() {
            var dom = fragment(
                element("p", "Paragraph"),
                element("table", { "class": "wiki" },
                    element("tbody",
                        element("tr", element("td", "1.1"), element("td", "1.2", { colSpan: 2 })),
                        element("tr", element("td", "2.1", { colSpan: 3 })),
                        element("tr",
                            element("td", "3.1"),
                            element("td", element("u", "3.2")),
                            element("td", element("tt", "3.3"))))),
                element("p", "Paragraph"));
            generateFragment.call(this, dom, [
                "Paragraph",
                "||1.1||||1.2",
                "||||||2.1",
                "||3.1||__3.2__||`3.3`",
                "Paragraph" ].join("\n"));
            generate.call(this, dom, [
                "Paragraph",
                "",
                "|| 1.1 |||| 1.2 ||",
                "|||||| 2.1 ||",
                "|| 3.1 || __3.2__ || `3.3` ||",
                "",
                "Paragraph" ].join("\n"));
        });

        unit.add("table header", function() {
            var dom = fragment(
                element("p", "Paragraph"),
                element("table", { "class": "wiki" },
                    element("tbody",
                        element("tr", element("th", "1.1"), element("td", "1.2", { colSpan: 2 })),
                        element("tr", element("th", "2.1", { colSpan: 3 })),
                        element("tr",
                            element("td", "3.1"),
                            element("th", element("u", "3.2")),
                            element("td", element("tt", "3.3"))))),
                element("p", "Paragraph"));
            generateFragment.call(this, dom, [
                "Paragraph",
                "||=1.1=||||1.2",
                "||||||=2.1=||",
                "||3.1||=__3.2__=||`3.3`",
                "Paragraph" ].join("\n"));
            generate.call(this, dom, [
                "Paragraph",
                "",
                "||= 1.1 =|||| 1.2 ||",
                "||||||= 2.1 =||",
                "|| 3.1 ||= __3.2__ =|| `3.3` ||",
                "",
                "Paragraph" ].join("\n"));
        });

        unit.add("table with alignment", function() {
            var dom = fragment(
                element("p", "Paragraph"),
                element("table", { "class": "wiki" },
                    element("tbody",
                        element("tr", element("th", "1.1"),
                        element("td", "1.2", { colSpan: 2, align: "right" })),
                        element("tr", element("th", "2.1", { colSpan: 3, align: "left" })),
                        element("tr",
                            element("td", "3||1", { align: "right" }),
                            element("th", element("u", "3.2")),
                            element("td", element("tt", "3.3"), { align: "left" })),
                        element("tr",
                            element("th", "4.1", { align: "center" }),
                            element("td", "4.2"),
                            element("td", "4.3", { align: "center" })))),
                element("p", "Paragraph"));
            generateFragment.call(this, dom, [
                "Paragraph",
                "||=1.1=|||| 1.2",
                "||||||=2.1 =||",
                "|| 3!||1||= __3.2__ =||`3.3` ||",
                "||=  4.1     =|| 4.2 ||    4.3    ||",
                "Paragraph" ].join("\n"));
            generate.call(this, dom, [
                "Paragraph",
                "",
                "||= 1.1 =|||| 1.2||",
                "||||||=2.1 =||",
                "|| 3!||1||= __3.2__ =||`3.3` ||",
                "||=  4.1  =|| 4.2 ||  4.3  ||",
                "",
                "Paragraph" ].join("\n"));
        });

        unit.add("table with row continuation", function() {
            var dom = fragment(
                element("p", "Paragraph"),
                element("table", { "class": "wiki" },
                    element("tbody",
                        element("tr", element("td", "1.1"), element("td", "1.2"), element("td", "1.3")),
                        element("tr", element("td", "2.1")),
                        element("tr",
                            element("td", "3.1"),
                            element("td", element("u", "3.2")),
                            element("td", element("tt", "3.3"))))),
                element("p", "Paragraph"));
            generateFragment.call(this, dom, [
                "Paragraph",
                "||1.1||1.2||    \\",
                "||1.3",
                "||2.1",
                "||3.1||__3.2__||`3.3`||\\",
                "Paragraph" ].join("\n"));
        });

        unit.add("table + rule", function() {
            var dom = fragment(
                element("table", { "class": "wiki" },
                    element("tbody", element("tr", element("td", "1st")))),
                element("p", element("b", "bold")),
                element("table", { "class": "wiki" },
                    element("tbody", element("tr", element("td", "2nd")))),
                element("p", "'''normal"));
            generateFragment.call(this, dom, [
                "||1st||",
                "'''bold'''",
                "||2nd||",
                "!'''normal" ].join("\n"));
            generate.call(this, dom, [
                "|| 1st ||",
                "",
                "'''bold'''",
                "",
                "|| 2nd ||",
                "",
                "!'''normal" ].join("\n"));
        });

        unit.add("blockquote + table", function() {
            var dom = fragment(
                element("p", "Paragraph"),
                element("table", { "class": "wiki" },
                    element("tbody",
                        element("tr", element("td", "pre.1"), element("td", "pre.2")))),
                element("blockquote",
                    element("table", { "class": "wiki" },
                        element("tbody",
                            element("tr", element("td", "1.1"), element("td", "1.2")),
                            element("tr", element("td", "2.1")))),
                    element("blockquote",
                        element("table", { "class": "wiki" },
                            element("tbody",
                                element("tr", element("td", "deep"))))),
                    element("table", { "class": "wiki" },
                        element("tbody",
                            element("tr",
                                element("td", "3.1"),
                                element("td", element("u", "3.2")),
                                element("td", element("tt", "3.3")))))),
                element("table", { "class": "wiki" },
                    element("tbody",
                        element("tr", element("td", "post.1"), element("td", "post.2")))),
                element("p", "Paragraph"));
            generateFragment.call(this, dom, [
                "Paragraph",
                "||pre.1||pre.2||",
                " ||1.1||1.2||",
                " ||2.1",
                "  ||deep||",
                " ||3.1||__3.2__||`3.3`",
                "||post.1||post.2||",
                "Paragraph" ].join("\n"));
            generate.call(this, dom, [
                "Paragraph",
                "",
                "|| pre.1 || pre.2 ||",
                "",
                "  || 1.1 || 1.2 ||",
                "  || 2.1 ||",
                "    || deep ||",
                "  || 3.1 || __3.2__ || `3.3` ||",
                "",
                "|| post.1 || post.2 ||",
                "",
                "Paragraph" ].join("\n"));
        });

        unit.add("table [ paragraph, ul ]", function() {
            var dom = fragment(
                element("table", { "class": "wiki" },
                    element("tbody",
                        element("tr",
                            element("td", element("p", "1.1")),
                            element("td",
                                element("ul",
                                    element("li", "item 1"),
                                    element("li", "item 2")))),
                        element("tr",
                            element("td",
                                element("p", "2.1"),
                                element("ul",
                                    element("li", "item 3"),
                                    element("li", "item 4")))))));
            generateWikitext.call(this, dom, [
                "|| 1.1 || * item 1[[BR]] * item 2 ||",
                "|| 2.1[[BR]][[BR]] * item 3[[BR]] * item 4 ||" ].join("\n"));
        });

        unit.add("table from word", function() {
            var dom = element("div");
            dom.innerHTML = [
                '',
                '<table class="MsoTableGrid" style="border: medium none ; border-collapse: collapse;" border="1" cellpadding="0" cellspacing="0">',
                ' <tbody><tr style="">',
                '  <td style="border: 1pt solid windowtext; padding: 0mm 5.4pt; width: 217.55pt;" valign="top" width="290">',
                '  <p class="MsoNormal"><span lang="EN-US">a<o:p></o:p></span></p>',
                '  <p class="MsoNormal"><span lang="EN-US">b<o:p></o:p></span></p>',
                '  </td>',
                '  <td style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0mm 5.4pt; width: 217.55pt;" valign="top" width="290">',
                '',
                '  <p class="MsoNormal"><span lang="EN-US">b<o:p></o:p></span></p>',
                '  </td>',
                ' </tr>',
                ' <tr style="">',
                '  <td style="border-style: none solid solid; border-color: -moz-use-text-color windowtext windowtext; border-width: medium 1pt 1pt; padding: 0mm 5.4pt; width: 217.55pt;" valign="top" width="290">',
                '  <p class="MsoNormal"><span lang="EN-US">c<o:p></o:p></span></p>',
                '  </td>',
                '  <td style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0mm 5.4pt; width: 217.55pt;" valign="top" width="290">',
                '',
                '  <p class="MsoNormal"><span lang="EN-US">d<o:p></o:p></span></p>',
                '  </td>',
                ' </tr>',
                '</tbody></table>',
                '' ].join("\n");
            generateWikitext.call(this, dom, [
                "|| a[[BR]][[BR]]b || b ||",
                "|| c || d ||" ].join("\n"));
        });

        unit.add("domToWikitext for code block", function() {
            var br = function() { return element("br") };
            var dom = fragment(
                element("h1", "Heading", br(), "1"),
                element("h2", "Heading", br(), "2"),
                element("h3", "Heading", br(), "3"),
                element("h4", "Heading", br(), "4"),
                element("h5", "Heading", br(), "5"),
                element("h6", "Heading", br(), "6"),
                element("p",
                    "var TracWysiwyg = function(textarea) {", br(),
                    "...", br(),
                    "}"),
                element("blockquote", { "class": "citation" }, element("p", "citation", br(), "continued")),
                element("blockquote", element("p", "quote", br(), "continued")),
                element("ul",
                    element("li", "item 1", br(), "continued"),
                    element("ol", element("li", "item", br(), "1.1"))),
                element("dl",
                    element("dt", "def to_s(", br(), ")"),
                    element("dd", "dt", br(), "dd")),
                element("table",
                    element("tbody",
                        element("tr",
                            element("td", "cell", br(), "1"),
                            element("th", "cell", br(), "2")))));
            var wikitext = instance.domToWikitext(dom, { formatCodeBlock: true });
            this.assertEqual([
                "= Heading 1 =",
                "== Heading 2 ==",
                "=== Heading 3 ===",
                "==== Heading 4 ====",
                "===== Heading 5 =====",
                "====== Heading 6 ======",
                "var TracWysiwyg = function(textarea) {",
                "...",
                "}",
                "",
                "> citation",
                "> continued",
                "",
                "  quote",
                "  continued",
                "",
                " * item 1",
                "   continued",
                "   1. item",
                "     1.1",
                "",
                " def to_s( ):: dt",
                "    dd",
                "",
                "|| cell[[BR]]1 ||= cell[[BR]]2 =||" ].join("\n"), wikitext);
        });

        unit.add("escape newlines", function() {
            var dom = fragment(
                element("h1", "header"),
                element("blockquote", { "class": "citation" },
                    element("p",
                        br(),
                        "preserve", br(),
                        "newlines", br(),
                        br(),
                        element("i", "(since 0.11)"), br(),
                        br(),
                        br())),
                element("p",
                    "Whether Wiki formatter should respect the new lines present", br(),
                    "in the Wiki text. If set to ", element("b", "default"), ", this is equivalent to", br(),
                    element("i", "yes"), " for new environments but keeps the old behavior for", br(),
                    "upgraded environments (i.e. 'no')."),
                element("p", "must_preserve_newlines"),
                element("ul",
                    element("li", "first", br(), "word"),
                    element("li", "second", br(), "word")),
                element("dl",
                    element("dt", "trac"),
                    element("dd", "trac.edgewall.org", br(), "trac-hacks.org")),
                element("table", { "class": "wiki" },
                    element("tbody",
                        element("tr",
                            element("td", "cell", br(), "cell")))));
            generate.call(this, dom, [
                "= header =",
                "> ",
                "> preserve",
                "> newlines",
                "> ",
                "> ''(since 0.11)''",
                "> ",
                "> ",
                "",
                "Whether Wiki formatter should respect the new lines present",
                "in the Wiki text. If set to '''default''', this is equivalent to",
                "''yes'' for new environments but keeps the old behavior for",
                "upgraded environments (i.e. 'no').",
                "",
                "must_preserve_newlines",
                "",
                " * first[[BR]]word",
                " * second[[BR]]word",
                "",
                " trac:: trac.edgewall.org[[BR]]trac-hacks.org",
                "",
                "|| cell[[BR]]cell ||" ].join("\n"), { escapeNewlines: true });
        });

        unit.add("selectRange", function() {
            var d = instance.contentDocument;
            function _element() {
                var args = [ d ];
                args.push.apply(args, arguments);
                return element.apply(this, args);
            }
            function _text() {
                var args = [ d ];
                args.push.apply(args, arguments);
                return text.apply(this, args);
            }
            function assertRangeText(expected, start, startOffset, end, endOffset) {
                instance.selectRange(start, startOffset, end, endOffset);
                if (expected instanceof RegExp) {
                    unit.assertMatch(expected, instance.getSelectionText());
                }
                else {
                    unit.assertEqual(expected, instance.getSelectionText());
                }
            }
            var body = d.body;
            while (body.childNodes.length > 0) {
                body.removeChild(body.lastChild);
            }
            body.appendChild(fragment(d,
                _element("p",
                    "The", " quick", " brown",
                    _element("b", " fox", " jumps", " over"),
                    " the", " lazy", " dog."),
                _element("p", "Brick ", "quiz ", "whangs ", "jumpy ", "veldt ", "fox.")));

            var paragraph1 = body.childNodes[0];
            var paragraph2 = body.childNodes[1];
            var bold = paragraph1.childNodes[3];
            assertRangeText("The", paragraph1.childNodes[0], 0, paragraph1.childNodes[0], 3);
            assertRangeText("he", paragraph1.childNodes[0], 1, paragraph1.childNodes[0], 3);
            assertRangeText("e quick brow", paragraph1.childNodes[0], 2, paragraph1.childNodes[2], 5);
            assertRangeText("ick brown", paragraph1.childNodes[1], 3, paragraph1.childNodes[2], 6);
            assertRangeText("ick brown fox j", paragraph1.childNodes[1], 3, bold.childNodes[1], 2);
            assertRangeText("ver the laz", bold.childNodes[2], 2, paragraph1.childNodes[5], 4);
            assertRangeText(" the lazy", paragraph1.childNodes[4], 0, paragraph1.childNodes[5], 5);
            assertRangeText("lazy dog.", paragraph1.childNodes[5], 1, paragraph1.childNodes[6], 5);
            assertRangeText(/^fox jumps over the lazy dog\.[\r\n]*Brick quiz whangs$/,
                bold.childNodes[0], 1, paragraph2.childNodes[2], 6);
            assertRangeText(" fox jumps over", paragraph1, 3, paragraph1, 4);
            assertRangeText(" dog.", paragraph1, 6, paragraph1, 7);
            assertRangeText("", paragraph1, 7, paragraph1, 7);
            assertRangeText("quick brown fox jumps over", paragraph1.childNodes[1], 1, paragraph1, 4);
            assertRangeText(" fox jumps over t", paragraph1, 3, paragraph1.childNodes[4], 2);
        });

        unit.run();
    }

    var button = document.createElement("button");
    button.innerHTML = "run &#187;";
    button.style.textDecoration = "underline";
    document.body.appendChild(button);
    addEvent(button, "click", run);
    button.focus();
});
