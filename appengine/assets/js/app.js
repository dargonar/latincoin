var oCurrentTable = {};

function genericFnStopLoading(id) {
    //console.debug(id);
    var el = $('#'+id).parents(".portlet");
    App.unblockUI(el);
}

function genericFnServerData(sSource, aoData, fnCallback ) {
    
    var myid = $(this).attr('id');

    $.ajax({
        'dataType': 'json',
        'type': 'POST',
        'url': sSource,
        'cache': false,
        'data': aoData,
        'success': [fnCallback,function(){ /*console.debug('calling genericFnStopLoading');*/ genericFnStopLoading(myid); }]
    });
}

$.fn.dataTableExt.oApi.fnReloadAjax = function ( oSettings, sNewSource, fnCallback, bStandingRedraw )
{
    // console.debug(oSettings);
    // console.debug(sNewSource);
    // console.debug(fnCallback);

    if ( sNewSource !== undefined && sNewSource !== null ) {
        oSettings.sAjaxSource = sNewSource;
    }
 
    // Server-side processing should just call fnDraw
    if ( oSettings.oFeatures.bServerSide ) {
        this.fnDraw();
        return;
    }
 
    this.oApi._fnProcessingDisplay( oSettings, true );
    var that = this;
    var iStart = oSettings._iDisplayStart;
    var aData = [];
 
    this.oApi._fnServerParams( oSettings, aData );

    oSettings.fnServerData.call( oSettings.oInstance, oSettings.sAjaxSource, aData, function(json) {
        /* Clear the old information from the table */
        that.oApi._fnClearTable( oSettings );
 
        /* Got the data - add it to the table */
        var aData =  (oSettings.sAjaxDataProp !== "") ?
            that.oApi._fnGetObjectDataFn( oSettings.sAjaxDataProp )( json ) : json;
 
        for ( var i=0 ; i<aData.length ; i++ )
        {
            that.oApi._fnAddData( oSettings, aData[i] );
        }
         
        oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
 
        that.fnDraw();
 
        if ( bStandingRedraw === true )
        {
            oSettings._iDisplayStart = iStart;
            that.oApi._fnCalculateEnd( oSettings );
            that.fnDraw( false );
        }
 
        that.oApi._fnProcessingDisplay( oSettings, false );

        /* Callback user function - for event handlers etc */
        if ( typeof fnCallback == 'function' && fnCallback !== null )
        {
            fnCallback( oSettings );
        }

    }, oSettings );
};

/*$.fn.dataTableExt.oApi.fnReloadAjax = function ( oSettings, sNewSource, fnCallback ){
    if ( typeof sNewSource != 'undefined' ){
        oSettings.sAjaxSource = sNewSource;
    }
    this.oApi._fnProcessingDisplay( oSettings, true );
    var that = this;
     
    oSettings.fnServerData( oSettings.sAjaxSource, null, function(json) {
        that.oApi._fnClearTable( oSettings );
         
        for ( var i=0 ; i<json.aaData.length ; i++ ){
            that.oApi._fnAddData( oSettings, json.aaData[i] );
        }
         
        oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
        that.fnDraw( that );
        that.oApi._fnProcessingDisplay( oSettings, false );
         
        if ( typeof fnCallback == 'function' ){
            fnCallback( oSettings );
        }
    });
}
*/
var App = function () {

    var isIE8 = false; // IE8 mode
    var currentPage = ''; // current page

    // useful function to make equal height for contacts stand side by side
    var setEqualHeight = function(columns) { 
        var tallestColumn = 0;
        columns = jQuery(columns);
        columns.each(function() {
            var currentHeight = $(this).height();
            if (currentHeight > tallestColumn) {
                tallestColumn = currentHeight;
            }
        });
        columns.height(tallestColumn);
    }

    // this function handles responsive layout on screen size resize or mobile device rotate.
    var handleResponsive = function () {
        if (jQuery.browser.msie && jQuery.browser.version.substr(0, 1) == 8) {
            isIE8 = true; // checkes for IE8 browser version
            $('.visible-ie8').show(); //
        }

        var isIE10 = !! navigator.userAgent.match(/MSIE 10/);

        if (isIE10) {
            jQuery('html').addClass('ie10'); // set ie10 class on html element.
        }

        // loops all page elements with "responsive" class and applied classes for tablet mode
        // For metornic  1280px or less set as tablet mode to display the content properly
        var handleTabletElements = function () {
            if ($(window).width() <= 1280) {
                $(".responsive").each(function () {
                    var forTablet = $(this).attr('data-tablet');
                    var forDesktop = $(this).attr('data-desktop');
                    if (forTablet) {
                        $(this).removeClass(forDesktop);
                        $(this).addClass(forTablet);
                    }
                });
                handleTooltip();
            }
        }

        // loops all page elements with "responsive" class and applied classes for desktop mode
        // For metornic  higher 1280px set as desktop mode to display the content properly
        var handleDesktopElements = function () {
            if ($(window).width() > 1280) {
                $(".responsive").each(function () {
                    var forTablet = $(this).attr('data-tablet');
                    var forDesktop = $(this).attr('data-desktop');
                    if (forTablet) {
                        $(this).removeClass(forTablet);
                        $(this).addClass(forDesktop);
                    }
                });
                handleTooltip();
            }
        }

        // handle all elements which require to re-initialize on screen width change(on resize or on rotate mobile device)
        var handleElements = function () {
            if (App.isPage("index")) {
                handleDashboardCalendar(); // handles full calendar for main page
                jQuery('.vmaps').each(function () {
                    var map = jQuery(this);
                    map.width(map.parent().width());
                });
            }

            if (App.isPage("charts")) {
                handleChartGraphs();
            }

            if (App.isPage("maps_vector")) { // jqvector maps requires to fix the width on screen resized.
                jQuery('.vmaps').each(function () {
                    var map = jQuery(this);
                    map.width(map.parent().width());
                });
            }

            if (App.isPage("calendar")) { // full calendar requires to fix the width on screen resized.
                handleCalendar();
            }

            if ($(window).width() < 900) { // remove sidebar toggler
                $.cookie('sidebar-closed', null);
                $('.page-container').removeClass("sidebar-closed");
            }

            handleTabletElements();
            handleDesktopElements();
        }

        // handles responsive breakpoints.
        $(window).setBreakpoints({
            breakpoints: [320, 480, 768, 900, 1024, 1280]
        });

        $(window).bind('exitBreakpoint320', function () {
            handleElements();
        });
        $(window).bind('enterBreakpoint320', function () {
            handleElements();
        });

        $(window).bind('exitBreakpoint480', function () {
            handleElements();
        });
        $(window).bind('enterBreakpoint480', function () {
            handleElements();
        });

        $(window).bind('exitBreakpoint768', function () {
            handleElements();
        });
        $(window).bind('enterBreakpoint768', function () {
            handleElements();
        });

        $(window).bind('exitBreakpoint900', function () {
            handleElements();
        });
        $(window).bind('enterBreakpoint900', function () {
            handleElements();
        });

        $(window).bind('exitBreakpoint1024', function () {
            handleElements();
        });
        $(window).bind('enterBreakpoint1024', function () {
            handleElements();
        });

        $(window).bind('exitBreakpoint1280', function () {
            handleElements();
        });
        $(window).bind('enterBreakpoint1280', function () {
            handleElements();
        });
    }

    var handleJQVMAP = function () {

        var showMap = function (name) {
            jQuery('.vmaps').hide();
            jQuery('#vmap_' + name).show();
        }

        var setMap = function (name) {
            var data = {
                map: 'world_en',
                backgroundColor: null,
                borderColor: '#333333',
                borderOpacity: 0.5,
                borderWidth: 1,
                color: '#c6c6c6',
                enableZoom: true,
                hoverColor: '#c9dfaf',
                hoverOpacity: null,
                values: sample_data,
                normalizeFunction: 'linear',
                scaleColors: ['#b6da93', '#909cae'],
                selectedColor: '#c9dfaf',
                selectedRegion: null,
                showTooltip: true,
                onLabelShow: function (event, label, code) {

                },
                onRegionOver: function (event, code) {
                    if (code == 'ca') {
                        event.preventDefault();
                    }
                },
                onRegionClick: function (element, code, region) {
                    var message = 'You clicked "' + region + '" which has the code: ' + code.toUpperCase();
                    alert(message);
                }
            };

            data.map = name + '_en';
            var map = jQuery('#vmap_' + name);
            if (!map) {
                return;
            }
            map.width(map.parent().parent().width());
            map.show();
            map.vectorMap(data);
            map.hide();
        }

        setMap("world");
        setMap("usa");
        setMap("europe");
        setMap("russia");
        setMap("germany");
        showMap("world");

        jQuery('#regional_stat_world').click(function () {
            showMap("world");
        });

        jQuery('#regional_stat_usa').click(function () {
            showMap("usa");
        });

        jQuery('#regional_stat_europe').click(function () {
            showMap("europe");
        });
        jQuery('#regional_stat_russia').click(function () {
            showMap("russia");
        });
        jQuery('#regional_stat_germany').click(function () {
            showMap("germany");
        });

        $('#region_statistics_loading').hide();
        $('#region_statistics_content').show();
    }

    var handleAllJQVMAP = function () {
        var setMap = function (name) {
            var data = {
                map: 'world_en',
                backgroundColor: null,
                borderColor: '#333333',
                borderOpacity: 0.5,
                borderWidth: 1,
                color: '#c6c6c6',
                enableZoom: true,
                hoverColor: '#c9dfaf',
                hoverOpacity: null,
                values: sample_data,
                normalizeFunction: 'linear',
                scaleColors: ['#b6da93', '#427d1a'],
                selectedColor: '#c9dfaf',
                selectedRegion: null,
                showTooltip: true,
                onRegionOver: function (event, code) {
                    //sample to interact with map
                    if (code == 'ca') {
                        event.preventDefault();
                    }
                },
                onRegionClick: function (element, code, region) {
                    //sample to interact with map
                    var message = 'You clicked "' + region + '" which has the code: ' + code.toUpperCase();
                    alert(message);
                }
            };

            data.map = name + '_en';
            var map = jQuery('#vmap_' + name);
            if (!map) {
                return;
            }
            map.width(map.parent().width());
            map.vectorMap(data);
        }

        setMap("world");
        setMap("usa");
        setMap("europe");
        setMap("russia");
        setMap("germany");
    }

    var handleDashboardCalendar = function () {

        if (!jQuery().fullCalendar) {
            return;
        }

        var date = new Date();
        var d = date.getDate();
        var m = date.getMonth();
        var y = date.getFullYear();

        var h = {};

        if ($('#calendar').width() <= 500) {
            $('#calendar').addClass("mobile");
            h = {
                left: 'title, prev, next',
                center: '',
                right: 'today,month,agendaWeek,agendaDay'
            };
        } else {
            //console.log("www");
            $('#calendar').removeClass("mobile");
            h = {
                left: 'title',
                center: '',
                right: 'prev,next,today,month,agendaWeek,agendaDay'
            };
        }

        $('#calendar').html("");
        $('#calendar').fullCalendar({
            disableDragging: true,
            header: h,
            editable: true,
            events: [{
                title: 'All Day Event',
                start: new Date(y, m, 1),
            }, {
                title: 'Long Event',
                start: new Date(y, m, d - 5),
                end: new Date(y, m, d - 2),
            }, {
                title: 'Repeating Event',
                start: new Date(y, m, d - 3, 16, 0),
                allDay: false,
            }, {
                title: 'Repeating Event',
                start: new Date(y, m, d + 4, 16, 0),
                allDay: false,
            }, {
                title: 'Meeting',
                start: new Date(y, m, d, 10, 30),
                allDay: false,
            }, {
                title: 'Lunch',
                start: new Date(y, m, d, 12, 0),
                end: new Date(y, m, d, 14, 0),
                allDay: false,
            }, {
                title: 'Birthday Party',
                start: new Date(y, m, d + 1, 19, 0),
                end: new Date(y, m, d + 1, 22, 30),
                allDay: false,
            }, {
                title: 'Click for Google',
                start: new Date(y, m, 28),
                end: new Date(y, m, 29),
                url: 'http://google.com/',
            }]
        });

    }

    var handleCalendar = function () {

        if (!jQuery().fullCalendar) {
            return;
        }

        var date = new Date();
        var d = date.getDate();
        var m = date.getMonth();
        var y = date.getFullYear();

        var h = {};
        if ($('#calendar').parents(".portlet").width() <= 720) {
            $('#calendar').addClass("mobile");
            h = {
                left: 'title, prev,next',
                center: '',
                right: 'today,month,agendaWeek,agendaDay'
            };
        } else {
            $('#calendar').removeClass("mobile");
            h = {
                left: 'title',
                center: '',
                right: 'prev,next,today,month,agendaWeek,agendaDay'
            };
        }

        var initDrag = function (el) {
            // create an Event Object (http://arshaw.com/fullcalendar/docs/event_data/Event_Object/)
            // it doesn't need to have a start or end
            var eventObject = {
                title: $.trim(el.text()) // use the element's text as the event title
            };
            // store the Event Object in the DOM element so we can get to it later
            el.data('eventObject', eventObject);
            // make the event draggable using jQuery UI
            el.draggable({
                zIndex: 999,
                revert: true, // will cause the event to go back to its
                revertDuration: 0 //  original position after the drag
            });
        }

        var addEvent = function (title) {
            title = title.length == 0 ? "Untitled Event" : title;
            var html = $('<div class="external-event label">' + title + '</div>');
            jQuery('#event_box').append(html);
            initDrag(html);
        }

        $('#external-events div.external-event').each(function () {
            initDrag($(this))
        });

        $('#event_add').unbind('click').click(function () {
            var title = $('#event_title').val();
            addEvent(title);
        });

        //predefined events
        $('#event_box').html("");
        addEvent("My Event 1");
        addEvent("My Event 2");
        addEvent("My Event 3");
        addEvent("My Event 4");
        addEvent("My Event 5");
        addEvent("My Event 6");

        $('#calendar').html("");
        $('#calendar').fullCalendar({
            header: h,
            editable: true,
            droppable: true, // this allows things to be dropped onto the calendar !!!
            drop: function (date, allDay) { // this function is called when something is dropped

                // retrieve the dropped element's stored Event Object
                var originalEventObject = $(this).data('eventObject');
                // we need to copy it, so that multiple events don't have a reference to the same object
                var copiedEventObject = $.extend({}, originalEventObject);

                // assign it the date that was reported
                copiedEventObject.start = date;
                copiedEventObject.allDay = allDay;
                copiedEventObject.className = $(this).attr("data-class");

                // render the event on the calendar
                // the last `true` argument determines if the event "sticks" (http://arshaw.com/fullcalendar/docs/event_rendering/renderEvent/)
                $('#calendar').fullCalendar('renderEvent', copiedEventObject, true);

                // is the "remove after drop" checkbox checked?
                if ($('#drop-remove').is(':checked')) {
                    // if so, remove the element from the "Draggable Events" list
                    $(this).remove();
                }
            },
            events: [{
                title: 'All Day Event',
                start: new Date(y, m, 1)
            }, {
                title: 'Long Event',
                start: new Date(y, m, d - 5),
                end: new Date(y, m, d - 2)
            }, {
                id: 999,
                title: 'Repeating Event',
                start: new Date(y, m, d - 3, 16, 0),
                allDay: false
            }, {
                id: 999,
                title: 'Repeating Event',
                start: new Date(y, m, d + 4, 16, 0),
                allDay: false
            }, {
                title: 'Meeting',
                start: new Date(y, m, d, 10, 30),
                allDay: false
            }, {
                title: 'Lunch',
                start: new Date(y, m, d, 12, 0),
                end: new Date(y, m, d, 14, 0),
                allDay: false
            }, {
                title: 'Birthday Party',
                start: new Date(y, m, d + 1, 19, 0),
                end: new Date(y, m, d + 1, 22, 30),
                allDay: false
            }, {
                title: 'Click for Google',
                start: new Date(y, m, 28),
                end: new Date(y, m, 29),
                url: 'http://google.com/'
            }]
        });

    }

    var handleMainMenu = function () {
        jQuery('.page-sidebar .has-sub > a').click(function () {

            var handleContentHeight = function() {
                var content = $('.page-content');
                var sidebar = $('.page-sidebar');

                if (!content.attr("data-height")) {
                    content.attr("data-height", content.height());
                }

                if (sidebar.height() > content.height()) {
                    content.height(sidebar.height() + 20);    
                } else {
                    content.height(content.attr("data-height"));
                }
            }

            var last = jQuery('.has-sub.open', $('.page-sidebar'));
            if (last.size() == 0) {
                //last = jQuery('.has-sub.active', $('.page-sidebar'));
            }
            last.removeClass("open");
            jQuery('.arrow', last).removeClass("open");
            jQuery('.sub', last).slideUp(200);

            var sub = jQuery(this).next();
            if (sub.is(":visible")) {
                jQuery('.arrow', jQuery(this)).removeClass("open");
                jQuery(this).parent().removeClass("open");
                sub.slideUp(200, function(){
                    handleContentHeight();
                });
            } else {
                jQuery('.arrow', jQuery(this)).addClass("open");
                jQuery(this).parent().addClass("open");
                sub.slideDown(200, function(){
                    handleContentHeight();
                });
            }
        });
    }

    var handleSidebarToggler = function () {

        var container = $(".page-container");

        if ($.cookie('sidebar-closed') == 1) {
            container.addClass("sidebar-closed");
        }

        // handle sidebar show/hide
        $('.page-sidebar .sidebar-toggler').click(function () {
            $(".sidebar-search").removeClass("open");
            var container = $(".page-container");
            if (container.hasClass("sidebar-closed") === true) {
                container.removeClass("sidebar-closed");
                $.cookie('sidebar-closed', null);
            } else {
                container.addClass("sidebar-closed");
                $.cookie('sidebar-closed', 1);
            }
            if (App.isPage("charts")) {
                setTimeout(function () {
                    handleChartGraphs();
                }, 100);
            }
        });

        // handle the search bar close
        $('.sidebar-search .remove').click(function () {
            $('.sidebar-search').removeClass("open");
        });

        // handle the search query submit on enter press
        $('.sidebar-search input').keypress(function (e) {
            if (e.which == 13) {
                window.location.href = "extra_search.html";
                return false; //<---- Add this line
            }
        });

        // handle the search submit
        $('.sidebar-search .submit').click(function () {
            if ($('.page-container').hasClass("sidebar-closed")) {
                if ($('.sidebar-search').hasClass('open') == false) {
                    $('.sidebar-search').addClass("open");
                } else {
                    window.location.href = "extra_search.html";
                }
            } else {
                window.location.href = "extra_search.html";
            }
        });
    }

    var handlePortletTools = function () {
        jQuery('.portlet .tools a.remove').click(function () {
            var removable = jQuery(this).parents(".portlet");
            if (removable.next().hasClass('portlet') || removable.prev().hasClass('portlet')) {
                jQuery(this).parents(".portlet").remove();
            } else {
                jQuery(this).parents(".portlet").parent().remove();
            }
        });

        jQuery('.portlet .tools a.reload').click(function () {
            
            var eid = $(this).attr('id');
            eid = eid.substr(0, eid.length-8);

            var el = jQuery(this).parents(".portlet");
            //console.debug('voy bloquard: ' + $(el))
            App.blockUI(el);

            oCurrentTable[eid].fnReloadAjax();
        });

        jQuery('.portlet .tools .collapse, .portlet .tools .expand').click(function () {
            var el = jQuery(this).parents(".portlet").children(".portlet-body");
            if (jQuery(this).hasClass("collapse")) {
                jQuery(this).removeClass("collapse").addClass("expand");
                el.slideUp(200);
            } else {
                jQuery(this).removeClass("expand").addClass("collapse");
                el.slideDown(200);
            }
        });

        /*
        sample code to handle portlet config popup on close
        $('#portlet-config').on('hide', function (e) {
            //alert(1);
            //if (!data) return e.preventDefault() // stops modal from being shown
        });
        */            
    }

    var handlePortletSortable = function () {
        if (!jQuery().sortable) {
            return;
        }

        $( "#sortable_portlets" ).sortable({
            connectWith: ".portlet",
            items: ".portlet",
            opacity: 0.8,
            coneHelperSize: true,
            placeholder: 'sortable-box-placeholder round-all',
            forcePlaceholderSize: true,
            tolerance: "pointer"
        });

        $( ".column" ).disableSelection();
       
    }

    var handleDashboardCharts = function () {

        if (!jQuery.plot) {
            return;
        }

        var data = [];
        var totalPoints = 250;

        // random data generator for plot charts
        function getRandomData() {
            if (data.length > 0) data = data.slice(1);
            // do a random walk
            while (data.length < totalPoints) {
                var prev = data.length > 0 ? data[data.length - 1] : 50;
                var y = prev + Math.random() * 10 - 5;
                if (y < 0) y = 0;
                if (y > 100) y = 100;
                data.push(y);
            }
            // zip the generated y values with the x values
            var res = [];
            for (var i = 0; i < data.length; ++i) res.push([i, data[i]])
            return res;
        }

        function showTooltip(title, x, y, contents) {
            $('<div id="tooltip" class="chart-tooltip"><div class="date">' + title + '<\/div><div class="label label-success">CTR: ' + x / 10 + '%<\/div><div class="label label-important">Imp: ' + x * 12 + '<\/div><\/div>').css({
                position: 'absolute',
                display: 'none',
                top: y - 100,
                width: 75,
                left: x - 40,
                border: '0px solid #ccc',
                padding: '2px 6px',
                'background-color': '#fff',
            }).appendTo("body").fadeIn(200);
        }

        function randValue() {
            return (Math.floor(Math.random() * (1 + 50 - 20))) + 10;
        }

        var pageviews = [
            [1, randValue()],
            [2, randValue()],
            [3, 2 + randValue()],
            [4, 3 + randValue()],
            [5, 5 + randValue()],
            [6, 10 + randValue()],
            [7, 15 + randValue()],
            [8, 20 + randValue()],
            [9, 25 + randValue()],
            [10, 30 + randValue()],
            [11, 35 + randValue()],
            [12, 25 + randValue()],
            [13, 15 + randValue()],
            [14, 20 + randValue()],
            [15, 45 + randValue()],
            [16, 50 + randValue()],
            [17, 65 + randValue()],
            [18, 70 + randValue()],
            [19, 85 + randValue()],
            [20, 80 + randValue()],
            [21, 75 + randValue()],
            [22, 80 + randValue()],
            [23, 75 + randValue()],
            [24, 70 + randValue()],
            [25, 65 + randValue()],
            [26, 75 + randValue()],
            [27, 80 + randValue()],
            [28, 85 + randValue()],
            [29, 90 + randValue()],
            [30, 95 + randValue()]
        ];

        var visitors = [
            [1, randValue() - 5],
            [2, randValue() - 5],
            [3, randValue() - 5],
            [4, 6 + randValue()],
            [5, 5 + randValue()],
            [6, 20 + randValue()],
            [7, 25 + randValue()],
            [8, 36 + randValue()],
            [9, 26 + randValue()],
            [10, 38 + randValue()],
            [11, 39 + randValue()],
            [12, 50 + randValue()],
            [13, 51 + randValue()],
            [14, 12 + randValue()],
            [15, 13 + randValue()],
            [16, 14 + randValue()],
            [17, 15 + randValue()],
            [18, 15 + randValue()],
            [19, 16 + randValue()],
            [20, 17 + randValue()],
            [21, 18 + randValue()],
            [22, 19 + randValue()],
            [23, 20 + randValue()],
            [24, 21 + randValue()],
            [25, 14 + randValue()],
            [26, 24 + randValue()],
            [27, 25 + randValue()],
            [28, 26 + randValue()],
            [29, 27 + randValue()],
            [30, 31 + randValue()]
        ];

        $('#site_statistics_loading').hide();
        $('#site_statistics_content').show();

        var plot_statistics = $.plot($("#site_statistics"), [{
            data: pageviews,
            label: "Unique Visits"
        }, {
            data: visitors,
            label: "Page Views"
        }], {
            series: {
                lines: {
                    show: true,
                    lineWidth: 2,
                    fill: true,
                    fillColor: {
                        colors: [{
                            opacity: 0.05
                        }, {
                            opacity: 0.01
                        }]
                    }
                },
                points: {
                    show: true
                },
                shadowSize: 2
            },
            grid: {
                hoverable: true,
                clickable: true,
                tickColor: "#eee",
                borderWidth: 0
            },
            colors: ["#d12610", "#37b7f3", "#52e136"],
            xaxis: {
                ticks: 11,
                tickDecimals: 0
            },
            yaxis: {
                ticks: 11,
                tickDecimals: 0
            }
        });

        var previousPoint = null;
        $("#site_statistics").bind("plothover", function (event, pos, item) {
            $("#x").text(pos.x.toFixed(2));
            $("#y").text(pos.y.toFixed(2));
            if (item) {
                if (previousPoint != item.dataIndex) {
                    previousPoint = item.dataIndex;

                    $("#tooltip").remove();
                    var x = item.datapoint[0].toFixed(2),
                        y = item.datapoint[1].toFixed(2);

                    showTooltip('24 Jan 2013', item.pageX, item.pageY, item.series.label + " of " + x + " = " + y);
                }
            } else {
                $("#tooltip").remove();
                previousPoint = null;
            }
        });

        //server load
        $('#load_statistics_loading').hide();
        $('#load_statistics_content').show();

        var updateInterval = 30;
        var plot_statistics = $.plot($("#load_statistics"), [getRandomData()], {
            series: {
                shadowSize: 1
            },
            lines: {
                show: true,
                lineWidth: 0.2,
                fill: true,
                fillColor: {
                    colors: [{
                        opacity: 0.1
                    }, {
                        opacity: 1
                    }]
                }
            },
            yaxis: {
                min: 0,
                max: 100,
                tickFormatter: function (v) {
                    return v + "%";
                }
            },
            xaxis: {
                show: false
            },
            colors: ["#e14e3d"],
            grid: {
                tickColor: "#a8a3a3",
                borderWidth: 0
            }
        });

        function statisticsUpdate() {
            plot_statistics.setData([getRandomData()]);
            plot_statistics.draw();
            setTimeout(statisticsUpdate, updateInterval);
        }
        statisticsUpdate();

        //site activities

        var previousPoint2 = null;
        $('#site_activities_loading').hide();
        $('#site_activities_content').show();

        var activities = [
            [1, 10],
            [2, 9],
            [3, 8],
            [4, 6],
            [5, 5],
            [6, 3],
            [7, 9],
            [8, 10],
            [9, 12],
            [10, 14],
            [11, 15],
            [12, 13],
            [13, 11],
            [14, 10],
            [15, 9],
            [16, 8],
            [17, 12],
            [18, 14],
            [19, 16],
            [20, 19],
            [21, 20],
            [22, 20],
            [23, 19],
            [24, 17],
            [25, 15],
            [25, 14],
            [26, 12],
            [27, 10],
            [28, 8],
            [29, 10],
            [30, 12],
            [31, 10],
            [32, 9],
            [33, 8],
            [34, 6],
            [35, 5],
            [36, 3],
            [37, 9],
            [38, 10],
            [39, 12],
            [40, 14],
            [41, 15],
            [42, 13],
            [43, 11],
            [44, 10],
            [45, 9],
            [46, 8],
            [47, 12],
            [48, 14],
            [49, 16],
            [50, 12],
            [51, 10]
        ];

        var plot_activities = $.plot(
        $("#site_activities"), [{
            data: activities,
            color: "rgba(107,207,123, 0.9)",
            shadowSize: 0,
            bars: {
                show: true,
                lineWidth: 0,
                fill: true,
                fillColor: {
                    colors: [{
                        opacity: 1
                    }, {
                        opacity: 1
                    }]
                }
            }
        }], {
            series: {
                bars: {
                    show: true,
                    barWidth: 0.9
                }
            },
            grid: {
                show: false,
                hoverable: true,
                clickable: false,
                autoHighlight: true,
                borderWidth: 0
            },
            yaxis: {
                min: 0,
                max: 20
            }
        });

        $("#site_activities").bind("plothover", function (event, pos, item) {
            $("#x").text(pos.x.toFixed(2));
            $("#y").text(pos.y.toFixed(2));
            if (item) {
                if (previousPoint2 != item.dataIndex) {
                    previousPoint2 = item.dataIndex;
                    $("#tooltip").remove();
                    var x = item.datapoint[0].toFixed(2),
                        y = item.datapoint[1].toFixed(2);
                    showTooltip('24 Feb 2013', item.pageX, item.pageY, x);
                }
            }
        });

        $('#site_activities, #load_statistics').bind("mouseleave", function () {
            $("#tooltip").remove();
        });
    }

    var handleOrderBookCharts = function () {

        if (!jQuery.plot) {
            return;
        }

        var data = [];
        var totalPoints = 250;

        // random data generator for plot charts
        function getRandomData() {
            if (data.length > 0) data = data.slice(1);
            // do a random walk
            while (data.length < totalPoints) {
                var prev = data.length > 0 ? data[data.length - 1] : 50;
                var y = prev + Math.random() * 10 - 5;
                if (y < 0) y = 0;
                if (y > 100) y = 100;
                data.push(y);
            }
            // zip the generated y values with the x values
            var res = [];
            for (var i = 0; i < data.length; ++i) res.push([i, data[i]])
            return res;
        }

        function do_order_book_graph() {
            // https://github.com/flot/flot/blob/master/API.md
            var plot = $.plot($("#order_book_graph"), 
            [{
                data: __bids,
                label: "Bids"
                    
            }, {
                data: __asks,
                label: "Asks"
                
            }], {
                series: {
                    lines: {
                        steps: true,
                        show: true,
                        lineWidth: 2,
                        fill: true,
                        fillColor: {
                            colors: [{
                                opacity: 0.09
                            }, {
                                opacity: 0.09
                            }]
                        }
                    },
                    points: {
                        show: false
                    },
                    shadowSize: 2
                },
                grid: {
                    hoverable: true,
                    clickable: true,
                    tickColor: "#eee",
                    borderWidth: 0
                },
                colors: ['#94c13e','#4e8cd9'],
                //colors: ["#d12610", "#37b7f3", "#52e136"],
                xaxis: {
                    ticks: 11,
                    tickDecimals: 4
                },
                yaxis://[{}, { position: "left", ticks: 11,tickDecimals: 0 }] 
                      {ticks: 11,tickDecimals: 0}
            });


            function showTooltip(x, y, contents) {
                $('<div id="tooltip">' + contents + '</div>').css({
                    position: 'absolute',
                    display: 'none',
                    top: y + 5,
                    left: x + 15,
                    border: '1px solid #333',
                    padding: '4px',
                    color: '#fff',
                    'border-radius': '3px',
                    'background-color': '#333',
                    opacity: 0.80
                }).appendTo("body").fadeIn(200);
            }

            var previousPoint = null;
            $("#order_book_graph").bind("plothover", function (event, pos, item) {
                $("#x").text(pos.x.toFixed(2));
                $("#y").text(pos.y.toFixed(2));

                if (item) {
                    if (previousPoint != item.dataIndex) {
                        previousPoint = item.dataIndex;

                        $("#tooltip").remove();
                        var x = item.datapoint[0].toFixed(2),
                            y = item.datapoint[1].toFixed(2);

                        showTooltip(item.pageX, item.pageY,   item.series.label+ ": " + item.datapoint[1] + " a $" + item.datapoint[0] );
                    }
                } else {
                    $("#tooltip").remove();
                    previousPoint = null;
                }
            });
        }

        do_order_book_graph();
        
    }

    var handleChartGraphs = function () {

        var graphData = [];
        var series = Math.floor(Math.random() * 10) + 2;
        for (var i = 0; i < series; i++) {
            graphData[i] = {
                label: "Series" + (i + 1),
                data: Math.floor((Math.random() - 1) * 100) + 1
            }
        }

        $.plot($("#graph_2"), graphData, {
            series: {
                pie: {
                    show: true,
                    radius: 1,
                    label: {
                        show: true,
                        radius: 3 / 4,
                        formatter: function (label, series) {
                            return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">' + label + '<br/>' + Math.round(series.percent) + '%</div>';
                        },
                        background: {
                            opacity: 0.5
                        }
                    }
                }
            },
            legend: {
                show: false
            }
        });
        
      
    }

    var handleFancyBox = function () {

        if (!jQuery.fancybox) {
            return;
        }

        if (jQuery(".fancybox-button").size() > 0) {
            jQuery(".fancybox-button").fancybox({
                groupAttr: 'data-rel',
                prevEffect: 'none',
                nextEffect: 'none',
                closeBtn: true,
                helpers: {
                    title: {
                        type: 'inside'
                    }
                }
            });
        }
    }

    var handleLoginForm = function () {
        //return;/* HACK */
        $('.login-form input').keypress(function (e) {
            if (e.which == 13) {
                window.location.href = "index.html";
                return false;
            }
        });

        jQuery('#forget-password').click(function () {
            jQuery('.login-form').hide();
            jQuery('.forget-form').show();
        });

        jQuery('#forget-btn, #back-btn').click(function () {
            jQuery('.login-form').show();
            jQuery('.forget-form').hide();
        });

        jQuery('#register-btn').click(function () {
            jQuery('.login-form').hide();
            jQuery('.register-form').show();
        });

        jQuery('#register-back-btn').click(function () {
            jQuery('.login-form').show();
            jQuery('.register-form').hide();
        });
    }

    var handleFixInputPlaceholderForIE = function () {
        //fix html5 placeholder attribute for ie7 & ie8
        if (jQuery.browser.msie && jQuery.browser.version.substr(0, 1) <= 9) { // ie7&ie8
            jQuery('input[placeholder], textarea[placeholder]').each(function () {

                var input = jQuery(this);

                jQuery(input).val(input.attr('placeholder'));

                jQuery(input).focus(function () {
                    if (input.val() == input.attr('placeholder')) {
                        input.val('');
                    }
                });

                jQuery(input).blur(function () {
                    if (input.val() == '' || input.val() == input.attr('placeholder')) {
                        input.val(input.attr('placeholder'));
                    }
                });
            });
        }
    }

    var handlePulsate = function () {
        if (!jQuery().pulsate) {
            return;
        }

        if (isIE8 == true) {
            return; // pulsate plugin does not support IE8 and below
        }

        if (jQuery().pulsate) {
            jQuery('#pulsate-regular').pulsate({
                color: "#bf1c56"
            });

            jQuery('#pulsate-once').click(function () {
                $(this).pulsate({
                    color: "#399bc3",
                    repeat: false
                });
            });

            jQuery('#pulsate-hover').pulsate({
                color: "#5ebf5e",
                repeat: false,
                onHover: true
            });

            jQuery('#pulsate-crazy').click(function () {
                $(this).pulsate({
                    color: "#fdbe41",
                    reach: 50,
                    repeat: 10,
                    speed: 100,
                    glow: true
                });
            });
        }
    }

    var handleIntro = function () {
        if ($.cookie('intro_show')) {
            return;
        }

        $.cookie('intro_show', 1);

        setTimeout(function () {
            var unique_id = $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'Meet Metronic!',
                // (string | mandatory) the text inside the notification
                text: 'Metronic is a brand new Responsive Admin Dashboard Template you have always been looking for!',
                // (string | optional) the image to display on the left
                image: './assets/img/avatar1.jpg',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: true,
                // (int | optional) the time you want it to be alive for before fading out
                time: '',
                // (string | optional) the class name you want to apply to that specific message
                class_name: 'my-sticky-class'
            });

            // You can have it return a unique id, this can be used to manually remove it later using
            setTimeout(function () {
                $.gritter.remove(unique_id, {
                    fade: true,
                    speed: 'slow'
                });
            }, 12000);
        }, 2000);

        setTimeout(function () {
            var unique_id = $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'Buy Metronic!',
                // (string | mandatory) the text inside the notification
                text: 'Metronic comes with a huge collection of reusable and easy customizable UI components and plugins. Buy Metronic today!',
                // (string | optional) the image to display on the left
                image: './assets/img/avatar1.jpg',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: true,
                // (int | optional) the time you want it to be alive for before fading out
                time: '',
                // (string | optional) the class name you want to apply to that specific message
                class_name: 'my-sticky-class'
            });

            // You can have it return a unique id, this can be used to manually remove it later using
            setTimeout(function () {
                $.gritter.remove(unique_id, {
                    fade: true,
                    speed: 'slow'
                });
            }, 13000);
        }, 8000);

        setTimeout(function () {

            $('#styler').pulsate({
                color: "#bb3319",
                repeat: 10
            });

            $.extend($.gritter.options, {
                position: 'top-left'
            });

            var unique_id = $.gritter.add({
                position: 'top-left',
                // (string | mandatory) the heading of the notification
                title: 'Customize Metronic!',
                // (string | mandatory) the text inside the notification
                text: 'Metronic allows you to easily customize the theme colors and layout settings.',
                // (string | optional) the image to display on the left
                image1: './assets/img/avatar1.png',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: true,
                // (int | optional) the time you want it to be alive for before fading out
                time: '',
                // (string | optional) the class name you want to apply to that specific message
                class_name: 'my-sticky-class'
            });

            $.extend($.gritter.options, {
                position: 'top-right'
            });

            // You can have it return a unique id, this can be used to manually remove it later using
            setTimeout(function () {
                $.gritter.remove(unique_id, {
                    fade: true,
                    speed: 'slow'
                });
            }, 15000);

        }, 23000);

        setTimeout(function () {

            $.extend($.gritter.options, {
                position: 'top-left'
            });

            var unique_id = $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'Notification',
                // (string | mandatory) the text inside the notification
                text: 'You have 3 new notifications.',
                // (string | optional) the image to display on the left
                image1: './assets/img/image1.jpg',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: true,
                // (int | optional) the time you want it to be alive for before fading out
                time: '',
                // (string | optional) the class name you want to apply to that specific message
                class_name: 'my-sticky-class'
            });

            setTimeout(function () {
                $.gritter.remove(unique_id, {
                    fade: true,
                    speed: 'slow'
                });
            }, 4000);

            $.extend($.gritter.options, {
                position: 'top-right'
            });

            var number = $('#header_notification_bar .badge').text();
            number = parseInt(number);
            number = number + 3;
            $('#header_notification_bar .badge').text(number);
            $('#header_notification_bar').pulsate({
                color: "#66bce6",
                repeat: 5
            });

        }, 40000);

        setTimeout(function () {

            $.extend($.gritter.options, {
                position: 'top-left'
            });

            var unique_id = $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'Inbox',
                // (string | mandatory) the text inside the notification
                text: 'You have 2 new messages in your inbox.',
                // (string | optional) the image to display on the left
                image1: './assets/img/avatar1.jpg',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: true,
                // (int | optional) the time you want it to be alive for before fading out
                time: '',
                // (string | optional) the class name you want to apply to that specific message
                class_name: 'my-sticky-class'
            });

            $.extend($.gritter.options, {
                position: 'top-right'
            });

            setTimeout(function () {
                $.gritter.remove(unique_id, {
                    fade: true,
                    speed: 'slow'
                });
            }, 4000);

            var number = $('#header_inbox_bar .badge').text();
            number = parseInt(number);
            number = number + 2;
            $('#header_inbox_bar .badge').text(number);
            $('#header_inbox_bar').pulsate({
                color: "#dd5131",
                repeat: 5
            });

        }, 60000);
    }

    var handleGritterNotifications = function () {
        if (!jQuery.gritter) {
            return;
        }
        $('#gritter-sticky').click(function () {
            var unique_id = $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'This is a sticky notice!',
                // (string | mandatory) the text inside the notification
                text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus eget tincidunt velit. Cum sociis natoque penatibus et <a href="#" style="color:#ccc">magnis dis parturient</a> montes, nascetur ridiculus mus.',
                // (string | optional) the image to display on the left
                image: './assets/img/avatar1.jpg',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: true,
                // (int | optional) the time you want it to be alive for before fading out
                time: '',
                // (string | optional) the class name you want to apply to that specific message
                class_name: 'my-sticky-class'
            });
            return false;
        });

        $('#gritter-regular').click(function () {

            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'This is a regular notice!',
                // (string | mandatory) the text inside the notification
                text: 'This will fade out after a certain amount of time. Vivamus eget tincidunt velit. Cum sociis natoque penatibus et <a href="#" style="color:#ccc">magnis dis parturient</a> montes, nascetur ridiculus mus.',
                // (string | optional) the image to display on the left
                image: './assets/img/avatar1.jpg',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false,
                // (int | optional) the time you want it to be alive for before fading out
                time: ''
            });

            return false;

        });

        $('#gritter-max').click(function () {

            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'This is a notice with a max of 3 on screen at one time!',
                // (string | mandatory) the text inside the notification
                text: 'This will fade out after a certain amount of time. Vivamus eget tincidunt velit. Cum sociis natoque penatibus et <a href="#" style="color:#ccc">magnis dis parturient</a> montes, nascetur ridiculus mus.',
                // (string | optional) the image to display on the left
                image: './assets/img/avatar1.jpg',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false,
                // (function) before the gritter notice is opened
                before_open: function () {
                    if ($('.gritter-item-wrapper').length == 3) {
                        // Returning false prevents a new gritter from opening
                        return false;
                    }
                }
            });
            return false;
        });

        $('#gritter-without-image').click(function () {
            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'This is a notice without an image!',
                // (string | mandatory) the text inside the notification
                text: 'This will fade out after a certain amount of time. Vivamus eget tincidunt velit. Cum sociis natoque penatibus et <a href="#" style="color:#ccc">magnis dis parturient</a> montes, nascetur ridiculus mus.'
            });

            return false;
        });

        $('#gritter-light').click(function () {

            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'This is a light notification',
                // (string | mandatory) the text inside the notification
                text: 'Just add a "gritter-light" class_name to your $.gritter.add or globally to $.gritter.options.class_name',
                class_name: 'gritter-light'
            });

            return false;
        });

        $("#gritter-remove-all").click(function () {

            $.gritter.removeAll();
            return false;

        });
    }

    var handleTooltip = function () {
        if (App.isTouchDevice()) { // if touch device, some tooltips can be skipped in order to not conflict with click events
            jQuery('.tooltips:not(.no-tooltip-on-touch-device)').tooltip();
        } else {
            jQuery('.tooltips').tooltip();
        }
    }

    var handlePopover = function () {
        jQuery('.popovers').popover();
    }

    var handleChoosenSelect = function () {
        if (!jQuery().chosen) {
            return;
        }
        $(".chosen").chosen();
        $(".chosen-with-diselect").chosen({
            allow_single_deselect: true
        });
    }

    var handleUniform = function () {
        if (!jQuery().uniform) {
            return;
        }
        var test = $("input[type=checkbox]:not(.toggle), input[type=radio]:not(.toggle, .star)");
        if (test) {
            test.uniform();
        }
    }

    var initUniform = function (els) {
        jQuery(els).each(function(){
            if ($(this).parents(".checker").size() == 0) {
                $(this).show();
                $(this).uniform();
            }
        });
    }

    var handleWysihtml5 = function () {
        if (!jQuery().wysihtml5) {
            return;
        }

        if ($('.wysihtml5').size() > 0) {
            $('.wysihtml5').wysihtml5();
        }
    }

    var handleToggleButtons = function () {
        if (!jQuery().toggleButtons) {
            return;
        }
        $('.basic-toggle-button').toggleButtons();
        $('.text-toggle-button').toggleButtons({
            width: 200,
            label: {
                enabled: "Lorem Ipsum",
                disabled: "Dolor Sit"
            }
        });
        $('.danger-toggle-button').toggleButtons({
            style: {
                // Accepted values ["primary", "danger", "info", "success", "warning"] or nothing
                enabled: "danger",
                disabled: "info"
            }
        });
        $('.info-toggle-button').toggleButtons({
            style: {
                enabled: "info",
                disabled: ""
            }
        });
        $('.success-toggle-button').toggleButtons({
            style: {
                enabled: "success",
                disabled: "info"
            }
        });
        $('.warning-toggle-button').toggleButtons({
            style: {
                enabled: "warning",
                disabled: "info"
            }
        });

        $('.height-toggle-button').toggleButtons({
            height: 100,
            font: {
                'line-height': '100px',
                'font-size': '20px',
                'font-style': 'italic'
            }
        });
    }

    var handleTables = function () {
        if (!jQuery().dataTable) {
            return;
        }

        // begin first table
        $('.jquery-table').dataTable({
            "sDom": "<'row-fluid'<'span6'f>r>t<'row-fluid'<'span4'l><'span4'i><'span4'p>>", //"sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
            "sPaginationType": "bootstrap",
            "oLanguage": {
                "sLengthMenu": "_MENU_ filas por pág.",
                "oPaginate": {
                    "sPrevious": "Ant.",
                    "sNext": "Sig."
                }
            },
            "aoColumnDefs": [{
                'bSortable': false,
                'aTargets': [0]
            }]
        });

        //jQuery('.jquery-table .dataTables_filter input').addClass("m-wrap medium"); // modify table search input
        jQuery('.dataTables_filter').parent(".span6 ").remove(); // delete table search input
        //jQuery('#sample_1_wrapper .dataTables_length select').addClass("m-wrap xsmall"); // modify table per page dropdown

        
    }

    var handleDepositTables = function (mode) {
        
        if (!jQuery().dataTable) {
            return;
        }
        
        var tid = 'my_'+mode+'_in_table';

        // begin first table
        oCurrentTable[tid] = $('#'+tid).dataTable({
            "fnServerData" : genericFnServerData,
            "bProcessing": true,
            "sAjaxSource": table_ajax_source[mode+'_in'],
            "sDom": "<'row-fluid'<'span6'f>r>t<'row-fluid'<'span4'l><'span4'i><'span4'p>>", //"sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
            "sPaginationType": "bootstrap",
            "oLanguage": {
                "sEmptyTable": "No hay depositos",
                "sInfoEmpty": " ",
                "sLengthMenu": "_MENU_ depositos por pág.",
                "sInfo": "Mostrando _START_ a _END_ de _TOTAL_ depositos",
                "oPaginate": {
                    "sPrevious": "Ant.",
                    "sNext": "Sig."
                }
            },
            "aoColumnDefs": [{
                'bSortable': true,
                'aTargets': [1]
            }]
        });

        jQuery('.dataTables_filter').parent(".span6 ").remove(); // delete table search input
    }


    var handleOrderTables = function (mode, type) {
        
        if (!jQuery().dataTable) {
            return;
        }
        
        var tid = 'my_'+mode+'_'+type+'_table';
        
        // begin first table
        oCurrentTable[tid] = $('#'+tid).dataTable({
            "fnServerData" : genericFnServerData,
            "bProcessing": true,
            "bServerSide": false,            
            "sAjaxSource": table_ajax_source[mode+'_'+type],
            "sDom": "<'row-fluid'<'span6'f>r>t<'row-fluid'<'span4'l><'span4'i><'span4'p>>", //"sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
            "sPaginationType": "bootstrap",
            "oLanguage": {
                "sEmptyTable": "Sin ordenes activas",
                "sInfoEmpty": " ",
                "sLengthMenu": "_MENU_ ordenes por pág.",
                "sInfo": "Mostrando _START_ a _END_ de _TOTAL_ ordenes",
                "oPaginate": {
                    "sPrevious": "Ant.",
                    "sNext": "Sig."
                }
            },
            "aoColumnDefs": [{'bSortable': false,'aTargets': [0,7]}
                            ,{'sWidth': '12.5%', 'aTargets': [1,2,3,4,5,6] }
                            ,{'sWidth': '10%', 'aTargets': [7] }
                            ,{'sWidth': '15%', 'aTargets': [0] }
                            ,{'sClass': 'right', 'aTargets': [3,4,5] }
                            ]
        });

        jQuery('.dataTables_filter').parent(".span6 ").remove(); // delete table search input
    }

    var handleAccOperationTables = function (id, source) {
        
        if (!jQuery().dataTable) {
            return;
        }
        
        // begin first table
        oCurrentTable[id] = $('#'+id).dataTable({
            "bProcessing": true,
            "sAjaxSource": source,
            "fnServerData" : genericFnServerData,
            "sDom": "<'row-fluid'<'span6'f>r>t<'row-fluid'<'span4'l><'span4'i><'span4'p>>", //"sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
            "sPaginationType": "bootstrap",
            "oLanguage": {
                "sEmptyTable": "Sin retiros",
                "sInfoEmpty": " ",
                "sLengthMenu": "_MENU_ retiros por pág.",
                "sInfo": "Mostrando _START_ a _END_ de _TOTAL_ retiro\s",
                "oPaginate": {
                    "sPrevious": "Ant.",
                    "sNext": "Sig."
                }
            },
            "aoColumnDefs": [{'bSortable': false,'aTargets': [0,5]},
                            {'sWidth': '10%', 'aTargets': [5] }]
        });

        jQuery('.dataTables_filter').parent(".span6 ").remove(); // delete table search input
    }
    
    var handleTablaBitcoins = function () {

        function restoreRow(oTable, nRow) {
            var aData = oTable.fnGetData(nRow);
            var jqTds = $('>td', nRow);

            for (var i = 0, iLen = jqTds.length; i < iLen; i++) {
                oTable.fnUpdate(aData[i], nRow, i, false);
            }

            oTable.fnDraw();
        }

        function editRow(oTable, nRow) {
            var aData = oTable.fnGetData(nRow);
            var jqTds = $('>td', nRow);
            jqTds[0].innerHTML = '<input type="text" class="m-wrap span10" name="address" value="' + aData[0] + '" />';
            jqTds[1].innerHTML = '<input type="text" class="m-wrap span10" name="description" value="' + aData[1] + '" />';
                        
            var attr = (aData[2] == 'new' ? 'data-mode="new"' : '');

            var save_link = '<a href="#" class="edit btn mini green"><i class="icon-save"></i>&nbsp;Guardar</a>';
            var cancel_link = '<a href="#" class="cancel btn mini red" '+ attr +'><i class="icon-cancel"></i>&nbsp;Cancelar</a>'
            jqTds[2].innerHTML = save_link + '&nbsp' + cancel_link;
        }
        
        function saveRow(oTable, nRow) {
            var jqInputs = $('input', nRow);
            oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);
            oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);
            oTable.fnUpdate('', nRow, 2, false);
            oTable.fnDraw();
            oTable.fnDraw(); // llamamos dos veces porque sino rompe el disegno.
        }
        
        var oTable = $('#tabla_direcciones_bitcoin').dataTable({
            "fnServerData" : genericFnServerData,
            "bProcessing": true,
            "sAjaxSource": table_ajax_btc_addresses_source,
            "sDom": "<'row-fluid'<'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
            //"sDom": "<'row-fluid'<'span6'f>r>t<'row-fluid'<'span4'l><'span4'i><'span4'p>>", //"sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
            //"sDom": '<"top"i>rt<"bottom"flp><"clear">'
            "sPaginationType": "bootstrap",
            "oLanguage": {
                "sEmptyTable": "No ha ingresado ninguna direccion",
                "sInfoEmpty": " ",
                "sLengthMenu": "_MENU_ Direcciones por pág.",
                "sInfo": "Mostrando _START_ a _END_ de _TOTAL_ Direcciones",
                "oPaginate": {
                    "sPrevious": "Ant.",
                    "sNext": "Sig."
                }
            },
            "aoColumns": [
                            { "sWidth": "40%" },
                            { "sWidth": "40%" },
                            { "sWidth": "20%", "sClass": "center"},
                        ],
        });
        
        oCurrentTable['tabla_direcciones_bitcoin'] = oTable;

        jQuery('#tabla_direcciones_bitcoin_wrapper .row-fluid').remove(); // modify table search input
        
        var xEditing = null;

        $('#tabla_direcciones_bitcoin_new').click(function (e) {
            e.preventDefault();

            if($("a[data-mode='new']").length !=0 )
                return;

            if (xEditing !== null) {
                return;          
            }

            var aiNew = oTable.fnAddData(
              ['', '', 'new']
            );

            var nRow = oTable.fnGetNodes(aiNew[0]);
            editRow(oTable, nRow);
            xEditing = nRow;
        });

        $('#tabla_direcciones_bitcoin a.delete').live('click', function (e) {
            e.preventDefault();

            if (confirm("Esta seguro que desa borrar esta dirección?") == false) {
                return;
            }

            var nRow = $(this).parents('tr')[0];
            oTable.fnDeleteRow(nRow);

            $.ajax({
              type: "GET",
              url: $(this).attr('href'),
              success: (function (data) {

              }),
              error: (function (request, status, error) {

              })
            });

            return false;
        });

        $('#tabla_direcciones_bitcoin a.cancel').live('click', function (e) {
            e.preventDefault();
            if ($(this).attr("data-mode") == "new") {
                var nRow = $(this).parents('tr')[0];
                oTable.fnDeleteRow(nRow);
            } else {
                restoreRow(oTable, xEditing);
            }
            
            xEditing = null;
        });

        $('#tabla_direcciones_bitcoin a.edit').live('click', function (e) {
            e.preventDefault();

            //Hay uno nuevo editandose y hacen click en un "edit" de otro row
            if($("a[data-mode='new']").length !=0 && this.innerHTML.indexOf("Guardar") == -1 )
                return;
            
            //console.debug('voy a guardar!');

            var nRow = $(this).parents('tr')[0];

            if (xEditing !== null && xEditing != nRow) {
                /* Currently editing - but not this row - restore the old before continuing to edit mode */
                restoreRow(oTable, xEditing);
                editRow(oTable, nRow);
                xEditing = nRow;
            } else if (xEditing == nRow && this.innerHTML.indexOf("Guardar") != -1)  {
                /* Editing this row and want to save it */
                var inputs = $('input', xEditing);
                
                var form = $('<form></form>').css('display','none' ).attr('id','hiddenForm' ).attr("name", 'hiddenForm'); 
                $.each(inputs,function(key,value){
                  $("<input type='text' value='"+$(value).val()+"' />")
                    .attr("id", $(value).attr('name'))
                    .attr("name", $(value).attr('name'))
                    .appendTo(form);
                });
                
                //HACKU:---saco la key del attr
                var tmp = oTable.fnGetData(xEditing);
                var regkey = /key="([^"]*)"/;
                var key = "";
                res = regkey.exec(tmp[2]);
                if(res !== null && res.length>1)
                    key=res[1];

                $("<input type='text' value='"+key+"' />")
                    .attr("id", 'key')
                    .attr("name", 'key')
                    .appendTo(form);
                //-----------------------

                var serializedData = $(form).serialize();
                $(form).remove();
                
                $.ajax({
                  type: "POST",
                  cache: false,
                  data: serializedData,
                  url: table_ajax_btc_address_post,
                  success: (function (data) {
                    saveRow(oTable, xEditing);
                    xEditing = null;
                    setTimeout("oCurrentTable['tabla_direcciones_bitcoin'].fnReloadAjax();", 500);
                  }),
                  error: (function (request, status, error) {
                    alert(request.responseText);
                  })
                });
                //alert("Updated! Do not forget to do some ajax to sync with backend :)");
            } else {
                /* No edit in progress - let's start one */
                editRow(oTable, nRow);
                xEditing = nRow;
            }
        });

    }



    var handleTablaCuentasBancarias = function () {

        function restoreRow(oTable, nRow) {
            var aData = oTable.fnGetData(nRow);
            var jqTds = $('>td', nRow);

            for (var i = 0, iLen = jqTds.length; i < iLen; i++) {
                oTable.fnUpdate(aData[i], nRow, i, false);
            }

            oTable.fnDraw();
        }

        function editRow(oTable, nRow) {
            var aData = oTable.fnGetData(nRow);
            var jqTds = $('>td', nRow);
            jqTds[0].innerHTML = '<input type="text" class="m-wrap span10" name="cbu" value="' + aData[0] + '" />';
            jqTds[1].innerHTML = '<input type="text" class="m-wrap span10" name="description" value="' + aData[1] + '" />';
                        
            var attr = (aData[2] == 'new' ? 'data-mode="new"' : '');

            var save_link = '<a href="#" class="edit btn mini green"><i class="icon-save"></i>&nbsp;Guardar</a>';
            var cancel_link = '<a href="#" class="cancel btn mini red" '+ attr +'><i class="icon-cancel"></i>&nbsp;Cancelar</a>'
            jqTds[2].innerHTML = save_link + '&nbsp' + cancel_link;
        }
        
        function saveRow(oTable, nRow) {
            var jqInputs = $('input', nRow);
            oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);
            oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);
            oTable.fnUpdate('', nRow, 2, false);
            oTable.fnDraw();
            oTable.fnDraw(); // llamamos dos veces porque sino rompe el disegno.
        }
        
        var oTable = $('#tabla_cuentas_bancarias').dataTable({
            "fnServerData" : genericFnServerData,
            "bProcessing": true,
            "sAjaxSource": table_ajax_bank_accounts_source,
            "sDom": "<'row-fluid'<'span6'f>r>t<'row-fluid'<'span4'l><'span4'i><'span4'p>>", //"sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
            "sPaginationType": "bootstrap",
            "oLanguage": {
                "sEmptyTable": "No ha ingresado ninguna cuenta",
                "sInfoEmpty": " ",
                "sLengthMenu": "_MENU_ Cuentas por pág.",
                "sInfo": "Mostrando _START_ a _END_ de _TOTAL_ Cuentas",
                "oPaginate": {
                    "sPrevious": "Ant.",
                    "sNext": "Sig."
                }
            },
            "aoColumns": [
                            { "sWidth": "40%" },
                            { "sWidth": "40%" },
                            { "sWidth": "20%", "sClass": "center"},
                        ],
        });
        
        oCurrentTable['tabla_cuentas_bancarias'] = oTable;
        
        jQuery('#tabla_cuentas_bancarias_wrapper .row-fluid').remove(); // modify table search input
        
        var xEditing = null;

        $('#tabla_cuentas_bancarias_new').click(function (e) {
            e.preventDefault();

            if($("a[data-mode='new']").length !=0 )
                return;

            if (xEditing !== null) {
                return;          
            }

            var aiNew = oTable.fnAddData(
              [ '', '', '','new']
            );

            var nRow = oTable.fnGetNodes(aiNew[0]);
            editRow(oTable, nRow);
            xEditing = nRow;
        });

        $('#tabla_cuentas_bancarias a.delete').live('click', function (e) {
            e.preventDefault();

            if (confirm("Esta seguro que desa borrar esta cuenta?") == false) {
                return;
            }

            var nRow = $(this).parents('tr')[0];
            oTable.fnDeleteRow(nRow);

            $.ajax({
              type: "GET",
              url: $(this).attr('href'),
              success: (function (data) {

              }),
              error: (function (request, status, error) {

              })
            });

            return false;
        });

        $('#tabla_cuentas_bancarias a.cancel').live('click', function (e) {
            e.preventDefault();
            if ($(this).attr("data-mode") == "new") {
                var nRow = $(this).parents('tr')[0];
                oTable.fnDeleteRow(nRow);
            } else {
                restoreRow(oTable, xEditing);
            }
            
            xEditing = null;
        });

        $('#tabla_cuentas_bancarias a.edit').live('click', function (e) {
            e.preventDefault();

            //Hay uno nuevo editandose y hacen click en un "edit" de otro row
            if($("a[data-mode='new']").length !=0 && this.innerHTML.indexOf("Guardar") == -1 )
                return;
            
            //console.debug('voy a guardar!');

            var nRow = $(this).parents('tr')[0];

            if (xEditing !== null && xEditing != nRow) {
                /* Currently editing - but not this row - restore the old before continuing to edit mode */
                restoreRow(oTable, xEditing);
                editRow(oTable, nRow);
                xEditing = nRow;
            } else if (xEditing == nRow && this.innerHTML.indexOf("Guardar") != -1)  {
                /* Editing this row and want to save it */
                var inputs = $('input', xEditing);
                
                var form = $('<form></form>').css('display','none' ).attr('id','hiddenForm' ).attr("name", 'hiddenForm'); 
                $.each(inputs,function(key,value){
                  $("<input type='text' value='"+$(value).val()+"' />")
                    .attr("id", $(value).attr('name'))
                    .attr("name", $(value).attr('name'))
                    .appendTo(form);
                });
                
                //HACKU:---saco la key del attr
                var tmp = oTable.fnGetData(xEditing);
                var regkey = /key="([^"]*)"/;
                var key = "";
                res = regkey.exec(tmp[2]);
                if(res !== null && res.length>1)
                    key=res[1];

                $("<input type='text' value='"+key+"' />")
                    .attr("id", 'key')
                    .attr("name", 'key')
                    .appendTo(form);
                //-----------------------

                var serializedData = $(form).serialize();
                $(form).remove();
                
                $.ajax({
                  type: "POST",
                  cache: false,
                  data: serializedData,
                  url: table_ajax_bank_account_post,
                  success: (function (data) {
                    saveRow(oTable, xEditing);
                    xEditing = null;
                    setTimeout("oCurrentTable['tabla_cuentas_bancarias'].fnReloadAjax();", 500);
                  }),
                  error: (function (request, status, error) {
                    alert(request.responseText);
                  })
                });
                //alert("Updated! Do not forget to do some ajax to sync with backend :)");
            } else {
                /* No edit in progress - let's start one */
                editRow(oTable, nRow);
                xEditing = nRow;
            }
        });
    }


    var handleTagsInput = function () {
        if (!jQuery().tagsInput) {
            return;
        }
        $('#tags_1').tagsInput({
            width: 'auto',
            'onAddTag': function () {
                alert(1);
            },
        });
        $('#tags_2').tagsInput({
            width: 240
        });
    }

    var handleDateTimePickers = function () {

        if (jQuery().datepicker) {
            $('.date-picker').datepicker();
        }

        if (jQuery().timepicker) {
            $('.timepicker-default').timepicker();
            $('.timepicker-24').timepicker({
                minuteStep: 1,
                showSeconds: true,
                showMeridian: false
            });
        }

        if (!jQuery().daterangepicker) {
            return;
        }

        $('.date-range').daterangepicker();

        $('#dashboard-report-range').daterangepicker({
            ranges: {
                'Today': ['today', 'today'],
                'Yesterday': ['yesterday', 'yesterday'],
                'Last 7 Days': [Date.today().add({
                    days: -6
                }), 'today'],
                'Last 30 Days': [Date.today().add({
                    days: -29
                }), 'today'],
                'This Month': [Date.today().moveToFirstDayOfMonth(), Date.today().moveToLastDayOfMonth()],
                'Last Month': [Date.today().moveToFirstDayOfMonth().add({
                    months: -1
                }), Date.today().moveToFirstDayOfMonth().add({
                    days: -1
                })]
            },
            opens: 'left',
            format: 'MM/dd/yyyy',
            separator: ' to ',
            startDate: Date.today().add({
                days: -29
            }),
            endDate: Date.today(),
            minDate: '01/01/2012',
            maxDate: '12/31/2014',
            locale: {
                applyLabel: 'Submit',
                fromLabel: 'From',
                toLabel: 'To',
                customRangeLabel: 'Custom Range',
                daysOfWeek: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
                monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
                firstDay: 1
            },
            showWeekNumbers: true,
            buttonClasses: ['btn-danger']
        },

        function (start, end) {
            App.blockUI(jQuery("#dashboard"));
            setTimeout(function () {
                App.unblockUI(jQuery("#dashboard"));
                $.gritter.add({
                    title: 'Dashboard',
                    text: 'Dashboard date range updated.'
                });
                App.scrollTo();
            }, 1000);
            $('#dashboard-report-range span').html(start.toString('MMMM d, yyyy') + ' - ' + end.toString('MMMM d, yyyy'));

        });

        $('#dashboard-report-range').show();

        $('#dashboard-report-range span').html(Date.today().add({
            days: -29
        }).toString('MMMM d, yyyy') + ' - ' + Date.today().toString('MMMM d, yyyy'));

        $('#form-date-range').daterangepicker({
            ranges: {
                'Today': ['today', 'today'],
                'Yesterday': ['yesterday', 'yesterday'],
                'Last 7 Days': [Date.today().add({
                    days: -6
                }), 'today'],
                'Last 30 Days': [Date.today().add({
                    days: -29
                }), 'today'],
                'This Month': [Date.today().moveToFirstDayOfMonth(), Date.today().moveToLastDayOfMonth()],
                'Last Month': [Date.today().moveToFirstDayOfMonth().add({
                    months: -1
                }), Date.today().moveToFirstDayOfMonth().add({
                    days: -1
                })]
            },
            opens: 'right',
            format: 'MM/dd/yyyy',
            separator: ' to ',
            startDate: Date.today().add({
                days: -29
            }),
            endDate: Date.today(),
            minDate: '01/01/2012',
            maxDate: '12/31/2014',
            locale: {
                applyLabel: 'Submit',
                fromLabel: 'From',
                toLabel: 'To',
                customRangeLabel: 'Custom Range',
                daysOfWeek: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
                monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
                firstDay: 1
            },
            showWeekNumbers: true,
            buttonClasses: ['btn-danger']
        },

        function (start, end) {
            $('#form-date-range span').html(start.toString('MMMM d, yyyy') + ' - ' + end.toString('MMMM d, yyyy'));
        });

        $('#form-date-range span').html(Date.today().add({
            days: -29
        }).toString('MMMM d, yyyy') + ' - ' + Date.today().toString('MMMM d, yyyy'));


        if (!jQuery().datepicker || !jQuery().timepicker) {
            return;
        }
    }

    var handleClockfaceTimePickers = function () {

        if (!jQuery().clockface) {
            return;
        }

        $('#clockface_1').clockface();

        $('#clockface_2').clockface({
            format: 'HH:mm',
            trigger: 'manual'
        });

        $('#clockface_2_toggle-btn').click(function (e) {
            e.stopPropagation();
            $('#clockface_2').clockface('toggle');
        });

        $('#clockface_3').clockface({
            format: 'H:mm'
        }).clockface('show', '14:30');
    }

    var handleColorPicker = function () {
        if (!jQuery().colorpicker) {
            return;
        }
        $('.colorpicker-default').colorpicker({
            format: 'hex'
        });
        $('.colorpicker-rgba').colorpicker();
    }

    var handleAccordions = function () {
        $(".accordion").collapse().height('auto');

        var lastClicked;

        //add scrollable class name if you need scrollable panes
        jQuery('.accordion.scrollable .accordion-toggle').click(function () {
            lastClicked = jQuery(this);
        }); //move to faq section

        jQuery('.accordion.scrollable').on('shown', function () {
            jQuery('html,body').animate({
                scrollTop: lastClicked.offset().top - 150
            }, 'slow');
        });
    }

    var handleScrollers = function () {

        var setPageScroller = function () {
            $('.main').slimScroll({
                size: '12px',
                color: '#a1b2bd',
                height: $(window).height(),
                allowPageScroll: true,
                alwaysVisible: true,
                railVisible: true
            });
        }

        /*
        //if (isIE8 == false) {
            $(window).resize(function(){
               setPageScroller(); 
            });
            setPageScroller();
        //} else {
            $('.main').removeClass("main");
        //}
        */

        $('.scroller').each(function () {
            $(this).slimScroll({
                //start: $('.blah:eq(1)'),
                size: '7px',
                color: '#a1b2bd',
                height: $(this).attr("data-height"),
                alwaysVisible: ($(this).attr("data-always-visible") == "1" ? true : false),
                railVisible: ($(this).attr("data-rail-visible") == "1" ? true : false),
                disableFadeOut: true
            });
        });

    }

    var handleSliders = function () {
        // basic
        $(".slider-basic").slider(); // basic sliders

        // snap inc
        $("#slider-snap-inc").slider({
            value: 100,
            min: 0,
            max: 1000,
            step: 100,
            slide: function (event, ui) {
                $("#slider-snap-inc-amount").text("$" + ui.value);
            }
        });

        $("#slider-snap-inc-amount").text("$" + $("#slider-snap-inc").slider("value"));

        // range slider
        $("#slider-range").slider({
            range: true,
            min: 0,
            max: 500,
            values: [75, 300],
            slide: function (event, ui) {
                $("#slider-range-amount").text("$" + ui.values[0] + " - $" + ui.values[1]);
            }
        });

        $("#slider-range-amount").text("$" + $("#slider-range").slider("values", 0) + " - $" + $("#slider-range").slider("values", 1));

        //range max

        $("#slider-range-max").slider({
            range: "max",
            min: 1,
            max: 10,
            value: 2,
            slide: function (event, ui) {
                $("#slider-range-max-amount").text(ui.value);
            }
        });

        $("#slider-range-max-amount").text($("#slider-range-max").slider("value"));

        // range min
        $("#slider-range-min").slider({
            range: "min",
            value: 37,
            min: 1,
            max: 700,
            slide: function (event, ui) {
                $("#slider-range-min-amount").text("$" + ui.value);
            }
        });

        $("#slider-range-min-amount").text("$" + $("#slider-range-min").slider("value"));

        // 
        // setup graphic EQ
        $("#slider-eq > span").each(function () {
            // read initial values from markup and remove that
            var value = parseInt($(this).text(), 10);
            $(this).empty().slider({
                value: value,
                range: "min",
                animate: true,
                orientation: "vertical"
            });
        });

        // vertical slider
        $("#slider-vertical").slider({
            orientation: "vertical",
            range: "min",
            min: 0,
            max: 100,
            value: 60,
            slide: function (event, ui) {
                $("#slider-vertical-amount").text(ui.value);
            }
        });
        $("#slider-vertical-amount").text($("#slider-vertical").slider("value"));

        // vertical range sliders
        $("#slider-range-vertical").slider({
            orientation: "vertical",
            range: true,
            values: [17, 67],
            slide: function (event, ui) {
                $("#slider-range-vertical-amount").text("$" + ui.values[0] + " - $" + ui.values[1]);
            }
        });

        $("#slider-range-vertical-amount").text("$" + $("#slider-range-vertical").slider("values", 0) + " - $" + $("#slider-range-vertical").slider("values", 1));
    }

    var handlKnobElements = function () {
        //knob does not support ie8 so skip it
        if (!jQuery().knob || isIE8) {
            return;
        }

        $(".knob").knob({
            'dynamicDraw': true,
            'thickness': 0.2,
            'tickColorizeValues': true,
            'skin': 'tron'
        });

        if ($(".knobify").size() > 0) {
            $(".knobify").knob({
                readOnly: true,
                skin: "tron",
                'width': 100,
                'height': 100,
                'dynamicDraw': true,
                'thickness': 0.2,
                'tickColorizeValues': true,
                'skin': 'tron',
                draw: function () {
                    // "tron" case
                    if (this.$.data('skin') == 'tron') {

                        var a = this.angle(this.cv) // Angle
                        ,
                            sa = this.startAngle // Previous start angle
                            ,
                            sat = this.startAngle // Start angle
                            ,
                            ea // Previous end angle
                            ,
                            eat = sat + a // End angle
                            ,
                            r = 1;

                        this.g.lineWidth = this.lineWidth;

                        this.o.cursor && (sat = eat - 0.3) && (eat = eat + 0.3);

                        if (this.o.displayPrevious) {
                            ea = this.startAngle + this.angle(this.v);
                            this.o.cursor && (sa = ea - 0.3) && (ea = ea + 0.3);
                            this.g.beginPath();
                            this.g.strokeStyle = this.pColor;
                            this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, sa, ea, false);
                            this.g.stroke();
                        }

                        this.g.beginPath();
                        this.g.strokeStyle = r ? this.o.fgColor : this.fgColor;
                        this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, sat, eat, false);
                        this.g.stroke();

                        this.g.lineWidth = 2;
                        this.g.beginPath();
                        this.g.strokeStyle = this.o.fgColor;
                        this.g.arc(this.xy, this.xy, this.radius - this.lineWidth + 1 + this.lineWidth * 2 / 3, 0, 2 * Math.PI, false);
                        this.g.stroke();

                        return false;

                    }
                }
            });
        }
    }

    var handleGoTop = function () {
        /* set variables locally for increased performance */
        jQuery('.footer .go-top').click(function () {
            App.scrollTo();
        });
    }

    var handleChat = function () {
        var cont = $('#chats');
        var list = $('.chats', cont);
        var form = $('.chat-form', cont);
        var input = $('input', form);
        var btn = $('.btn', form);

        var handleClick = function () {
            var text = input.val();
            if (text.length == 0) {
                return;
            }

            var time = new Date();
            var time_str = time.toString('MMM dd, yyyy HH:MM');
            var tpl = '';
            tpl += '<li class="out">';
            tpl += '<img class="avatar" alt="" src="assets/img/avatar1.jpg"/>';
            tpl += '<div class="message">';
            tpl += '<span class="arrow"></span>';
            tpl += '<a href="#" class="name">Bob Nilson</a>&nbsp;';
            tpl += '<span class="datetime">at ' + time_str + '</span>';
            tpl += '<span class="body">';
            tpl += text;
            tpl += '</span>';
            tpl += '</div>';
            tpl += '</li>';

            var msg = list.append(tpl);
            input.val("");
            $('.scroller', cont).slimScroll({
                scrollTo: list.height()
            });
        }

        btn.click(handleClick);
        input.keypress(function (e) {
            if (e.which == 13) {
                handleClick();
                return false; //<---- Add this line
            }
        });
    }

    var handleStyler = function () {

        var panel = $('.color-panel');

        $('.icon-color', panel).click(function () {
            $('.color-mode').show();
            $('.icon-color-close').show();
        });

        $('.icon-color-close', panel).click(function () {
            $('.color-mode').hide();
            $('.icon-color-close').hide();
        });

        $('li', panel).click(function () {
            var color = $(this).attr("data-style");
            setColor(color);
            $('.inline li', panel).removeClass("current");
            $(this).addClass("current");
        });

        $('input', panel).change(function () {
            setLayout();
        });

        var setColor = function (color) {
            $('#style_color').attr("href", "assets/css/style_" + color + ".css");
        }

        var setLayout = function () {
            if ($('input.header', panel).is(":checked")) {
                $("body").addClass("fixed-top");
                $(".header").addClass("navbar-fixed-top");
            } else {
                $("body").removeClass("fixed-top");
                $(".header").removeClass("navbar-fixed-top");
            }
        }
    }

    var handleFormWizards = function () {
        if (!jQuery().bootstrapWizard) {
            return;
        }

        // default form wizard
        $('#form_wizard_1').bootstrapWizard({
            'nextSelector': '.button-next',
            'previousSelector': '.button-previous',
            onTabClick: function (tab, navigation, index) {
                //alert('on tab click disabled');
                return false;
            },
            onNext: function (tab, navigation, index) {
                var total = navigation.find('li').length;
                var current = index + 1;
                // set wizard title
                $('.step-title', $('#form_wizard_1')).text('Paso ' + (index + 1) + ' de ' + total);
                // set done steps
                jQuery('li', $('#form_wizard_1')).removeClass("done");
                var li_list = navigation.find('li');
                for (var i = 0; i < index; i++) {
                    jQuery(li_list[i]).addClass("done");
                }

                if (current == 1) {
                    $('#form_wizard_1').find('.button-previous').hide();
                } else {
                    $('#form_wizard_1').find('.button-previous').show();
                }

                if (current >= total) {
                    $('#form_wizard_1').find('.button-next').hide();
                    $('#form_wizard_1').find('.button-submit').show();
                } else {
                    $('#form_wizard_1').find('.button-next').show();
                    $('#form_wizard_1').find('.button-submit').hide();
                }
                App.scrollTo($('.page-title'));
            },
            onPrevious: function (tab, navigation, index) {
                var total = navigation.find('li').length;
                var current = index + 1;
                // set wizard title
                $('.step-title', $('#form_wizard_1')).text('Paso ' + (index + 1) + ' de ' + total);
                // set done steps
                jQuery('li', $('#form_wizard_1')).removeClass("done");
                var li_list = navigation.find('li');
                for (var i = 0; i < index; i++) {
                    jQuery(li_list[i]).addClass("done");
                }

                if (current == 1) {
                    $('#form_wizard_1').find('.button-previous').hide();
                } else {
                    $('#form_wizard_1').find('.button-previous').show();
                }

                if (current >= total) {
                    $('#form_wizard_1').find('.button-next').hide();
                    $('#form_wizard_1').find('.button-submit').show();
                } else {
                    $('#form_wizard_1').find('.button-next').show();
                    $('#form_wizard_1').find('.button-submit').hide();
                }

                App.scrollTo($('.page-title'));
            },
            onTabShow: function (tab, navigation, index) {
                var total = navigation.find('li').length;
                var current = index + 1;
                var $percent = (current / total) * 100;
                $('#form_wizard_1').find('.bar').css({
                    width: $percent + '%'
                });
            }
        });

        $('#form_wizard_1').find('.button-previous').hide();
        $('#form_wizard_1 .button-submit').click(function () {
            //alert('Finished! Hope you like it :)');
        }).hide();
    }

    return {

        //main function to initiate template pages
        init: function () {
            handleResponsive(); // set and handle responsive
            // page level handlers
            if (App.isPage("index")) {
                handleDashboardCharts(); // handles plot charts for main page
                handleJQVMAP(); // handles vector maps for home page
                handleDashboardCalendar(); // handles full calendar for main page
                handleChat(); // handles chat samples
                //handleIntro(); // this is for demo purpose. you may enable or disable this function.
            }

            if (App.isPage("grids")) {
                handlePortletSortable(); // handles full calendars
            }

            if (App.isPage("calendar")) {
                handleCalendar(); // handles full calendars
            }

            if (App.isPage("maps_vector")) {
                handleAllJQVMAP(); // handles vector maps for interactive map page
            }

            if (App.isPage("order_book")) {
                handleOrderBookCharts();
                //handleCharts(); // handles plot charts
                //handleChartGraphs();
            }

            if (App.isPage("sliders")) {
                handleSliders();
                handlKnobElements()
            }

            if (App.isPage("profile")) {
                handleTablaCuentasBancarias(); // handle editable tables
                handleTablaBitcoins(); // handle editable tables
            }
            
            if (App.isPage("withdraw")) {
                handleAccOperationTables('acc_opers_btc_table', table_ajax_btc_acc_opers_source); // handle editable tables
                handleAccOperationTables('acc_opers_bank_table', table_ajax_bank_acc_opers_source); // handle editable tables
            }
            
            if (App.isPage("table_managed")) {
                //handleTables(); // handles data tables
            }
            
            if (App.isPage("trade_new")) {
                handleOrderTables('active','bid'); // handles data tables
                handleOrderTables('active','ask'); // handles data tables
            }
            
            if (App.isPage("trade_history")) {
                handleOrderTables('active','any'); // handles data tables
                handleOrderTables('inactive','any'); // handles data tables
            }
            
            if (App.isPage("deposit_btc")) {
                handleDepositTables('btc');
            }

            // global handlers
            handleChoosenSelect(); // handles bootstrap chosen dropdowns
            handleScrollers(); // handles slim scrolling contents
            handleUniform(); // handles uniform elements
            handleTagsInput() // handles tag input elements
            handleDateTimePickers(); //handles form timepickers
            handleClockfaceTimePickers(); //handles form clockface timepickers
            handleColorPicker(); // handles form color pickers            
            handlePortletTools(); // handles portlet action bar functionality(refresh, configure, toggle, remove)
            handlePulsate(); // handles pulsate functionality on page elements
            handleGritterNotifications(); // handles gritter notifications
            handleTooltip(); // handles bootstrap tooltips
            handlePopover(); // handles bootstrap popovers
            handleToggleButtons(); // handles form toogle buttons
            handleWysihtml5(); //handles WYSIWYG Editor           
            handleFancyBox(); // handles fancy box image previews
            handleStyler(); // handles style customer tool
            handleMainMenu(); // handles main menu
            handleSidebarToggler() // handles sidebar hide/show
            handleFixInputPlaceholderForIE(); // fixes/enables html5 placeholder attribute for IE9, IE8
            handleGoTop(); //handles scroll to top functionality in the footer
            handleAccordions(); //handles accordions
            handleFormWizards(); // handles form wizards
        },

        // login page setup
        initLogin: function () {
            handleLoginForm(); // handles login form
            handleUniform(); // // handles uniform elements
            handleFixInputPlaceholderForIE(); // fixes/enables html5 placeholder attribute for IE9, IE8
        },

        // wrapper function for page element pulsate
        pulsate: function (el, options) {
            var opt = jQuery.extend(options, {
                color: '#d12610', // set the color of the pulse
                reach: 15, // how far the pulse goes in px
                speed: 300, // how long one pulse takes in ms
                pause: 0, // how long the pause between pulses is in ms
                glow: false, // if the glow should be shown too
                repeat: 1, // will repeat forever if true, if given a number will repeat for that many times
                onHover: false // if true only pulsate if user hovers over the element
            });
            jQuery(el).pulsate(opt);
        },

        // wrapper function to scroll to an element
        scrollTo: function (el, offeset) {
             pos = el ? $(el).offset().top : 0;
             jQuery('html,body').animate({
                 scrollTop: pos + (offeset ? offeset : 0)
             }, 'slow');
        },

        // wrapper function to  block element(indicate loading)
        blockUI: function (el, loaderOnTop) {
            lastBlockedUI = el;
            jQuery(el).block({
                message: '<img src="/assets/img/loading.gif" align="absmiddle">',
                css: {
                    border: 'none',
                    padding: '2px',
                    backgroundColor: 'none'
                },
                overlayCSS: {
                    backgroundColor: '#000',
                    opacity: 0.05,
                    cursor: 'wait'
                }
            });
        },

        // wrapper function to  un-block element(finish loading)
        unblockUI: function (el) {
            jQuery(el).unblock({
                onUnblock: function () {
                    jQuery(el).removeAttr("style");
                }
            });
        },

        // public method to initialize uniform inputs
        initFancybox : function() {
            handleFancyBox();
        },

        initUniform : function(el) {
            initUniform(el);
        },

        // set map page
        setPage: function (name) {
            currentPage = name;
        },

        // check current page
        isPage: function (name) {
            return currentPage == name ? true : false;
        },

        // check for device touch support
        isTouchDevice: function () {
            try {
                document.createEvent("TouchEvent");
                return true;
            } catch (e) {
                return false;
            }
        }

    };

}();