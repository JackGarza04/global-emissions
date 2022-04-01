window.onload = function () {

	var chart = new CanvasJS.Chart("sectorPieChart", {
		exportEnabled: true,
		animationEnabled: true,
		title:{
			text: "Emissions Per Sector"
		},
		legend:{
			cursor: "pointer",
			itemclick: explodePie
		},
		data: [{
			type: "pie",
			showInLegend: true,
			startAngle: 30,
			toolTipContent: "{name}: <strong>{y}%</strong>",
			indexLabel: "{name} - {y}%",
			dataPoints: [
			{{ points }}
/* 				{ y: 26, name: "School Aid", },
				{ y: 20, name: "Medical Aid" },
				{ y: 5, name: "Debt/Capital" },
				{ y: 3, name: "Elected Officials" },
				{ y: 7, name: "University" },
				{ y: 17, name: "Executive" },
				{ y: 22, name: "Other Local Assistance"} */
			]
		}]
	});
	chart.render();
}

function explodePie (e) {
	if(typeof (e.dataSeries.dataPoints[e.dataPointIndex].exploded) === "undefined" || !e.dataSeries.dataPoints[e.dataPointIndex].exploded) {
		e.dataSeries.dataPoints[e.dataPointIndex].exploded = true;
	} else {
		e.dataSeries.dataPoints[e.dataPointIndex].exploded = false;
	}
	e.chart.render();

}