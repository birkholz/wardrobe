/* =========================================================
 * Bar Chart made by myself for My Outfits
 * http://myoutfits.co
 * You may use this however you want, it's unlicensed,
 * however, I'd love to see what you do with it!
 * Email me at brandonjbirkholz@gmail.com
 * ====================================================== */
var chart_rendering = false;
!function( $ ) {

	var BarChart = function(element, options){
		this.element = $(element);
		this.reverse = options.reverse || false;
		this.title = options.title || this.element.title || '';
		this.sections = options.sections;
		this.total_value = 0;
		this.fade_speed = 500;
		this.render_speed = 200;
		this.colors = options.colors || 'brights';
		this.fill();
	};

	BarChart.prototype = {
		constructor: BarChart,
		flip: function(){
			if (this.reverse == true) this.reverse = false;
			else this.reverse = true;
			this.fill();
		},
		fill: function(sects){
			if (arguments.length == 0) var sects = this.sections;
			var chart = this.element,
				chart_obj = this;
			chart.html('');
			this.total_value = 0;
			var brights = ['#FFF467', '#ACD372', '#7CC576', '#3BB878', '#1ABBB4', '#00BFF3', '#438CCA', '#5574B9', '#605CA8', '#855FA8', '#A763A8', '#F06EA9', '#F26D7D', '#F26C4F', '#F68E55', '#FBAF5C', '#FFF467', '#ACD372', '#7CC576', '#3BB878', '#1ABBB4', '#00BFF3', '#438CCA', '#5574B9', '#605CA8', '#855FA8', '#A763A8', '#F06EA9', '#F26D7D', '#F26C4F', '#F68E55', '#FBAF5C'];
			var pastels = ['#F7977A', '#F9AD81', '#FDC68A', '#FFF79A', '#C4DF9B', '#A2D39C', '#82CA9D', '#7BCDC8', '#6ECFF6', '#7EA7D8', '#8493CA', '#8882BE', '#A187BE', '#BC8DBF', '#F49AC2', '#F6989D', '#F7977A', '#F9AD81', '#FDC68A', '#FFF79A', '#C4DF9B', '#A2D39C', '#82CA9D', '#7BCDC8', '#6ECFF6', '#7EA7D8', '#8493CA', '#8882BE', '#A187BE', '#BC8DBF', '#F49AC2', '#F6989D'];
			if (this.colors == 'pastels') colors = pastels;
			else colors = brights;
			for (var i=0;i<sects.length;i++) {
				this.total_value += sects[i]['value'];
			}
			var sections = sects.sort(function(a, b){
				if (a['name'] > b['name']) return -1;
				if (a['name'] < b['name']) return 1;
				return 0;
			});
			sections.sort(function(a, b) {
				return a['value'] - b['value'];
			});
			var title = $('<div class="bar_title">'+this.title+'<div class="bar_total">'+this.total_value+'</div></div>');
			chart.append(title);
			if (chart.hasClass('drilldown')) {
				var drillout_button = $('<div title="return" class="glyphicon glyphicon-white"></div>');
				if (chart_obj.reverse) drillout_button.addClass('glyphicon-arrow-right');
				else drillout_button.addClass('glyphicon-arrow-left');
				title.html('').append(drillout_button);
				drillout_button.on('click', function(){
					chart.removeClass('drilldown');
					chart_obj.fill();
				});
			}
			// else {
			// 	var flip_button = $('<div title="flip horizontally" class="glyphicon glyphicon-resize-horizontal"></div>');
			// 	title.append(flip_button);
			// 	flip_button.on('click', function(){
			// 		chart_obj.flip();
			// 	});
			// }
			title.css('opacity', '0').animate({'opacity': '1'},chart_obj.fade_speed);
			if (this.reverse) {
				sections.reverse();
				colors.reverse();
				chart.addClass('reverse');
				var biggest_column = sections[0],
					biggest_height = biggest_column['value'];
			}
			else {
				chart.removeClass('reverse');
				var biggest_column = sections[sections.length-1],
					biggest_height = biggest_column['value'];
			}
			var next_pos = 0,
				width = (chart.innerWidth() - (sections.length - 1) * 2) / sections.length,
				multiplier = chart.innerHeight() / biggest_height,
				column = -1;
			(function column_writer(i) {
				setTimeout(function(){
					var section = sections[column],
						sec_name = section['name'],
						sec_height = section['value'] * multiplier,
						sec_width = width - 1,
						color = colors[column];
					if (sections.length < colors.length / 2 ) color = colors[column*2];
					if (sections.length < colors.length / 3 ) color = colors[column*3];
					var html = $('<div class="bar_container" style="left:'+next_pos+'px;width:'+ sec_width +'px;"><div class="bar_label">'+sec_name+'</div><div class="bar_section" style="background-color:'+color+';height:'+sec_height+'px;"><div class="bar_value"><span>'+section['value']+'</span></div></div></div>');
					next_pos += width + 2;
					chart.append(html);
					if (section['children']){
						html.on('click', function(){
							chart.addClass('drilldown');
							chart_obj.fill(section['children']);
						});
					}
					else html.addClass('no_children');
					html.css('opacity', '0').animate({'opacity': '1'},chart_obj.fade_speed);
					var max_label_height = (chart.outerHeight() / 4) * 3,
						label = html.find('.bar_value');
					if (section == biggest_column || sec_height > max_label_height) {
						html.addClass('biggest');
						label.css('margin-top', '-' + (label.outerHeight() / 2)+'px');
					}
					else if (sec_height < 20) label.append(' &#8595;');
					if (--i) column_writer(i);
				}, chart_obj.render_speed);
			column++;
			})(sections.length);
			chart_rendering = false;
		}
	};

	$.fn.barChart = function ( option, val ) {
		return this.each(function () {
			var $this = $(this),
				data = $this.data('barchart'),
				options = typeof option === 'object' && option;
			if (!data) {
				$this.data('barchart', (data = new BarChart(this, $.extend({},options))));
			}
			if (typeof option === 'string') data[option](val);
		});
	};

	$.fn.barChart.Constructor = BarChart;

}( window.jQuery );