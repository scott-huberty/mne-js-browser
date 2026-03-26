window.dash_clientside = Object.assign({}, window.dash_clientside, {
  mneJsBrowser: {
    toggleBadChannel: function(clickData, fig, badChannels) {
      var noUpdate = window.dash_clientside.no_update;
      if (!clickData || !clickData.points || clickData.points.length === 0 || !fig || !fig.data) {
        return noUpdate;
      }

      var point = clickData.points[0];
      var curveNumber = point.curveNumber;
      if (curveNumber === undefined || curveNumber === null) {
        return noUpdate;
      }

      var trace = fig.data[curveNumber];
      if (!trace || !trace.name) {
        return noUpdate;
      }

      var next = Array.isArray(badChannels) ? badChannels.slice() : [];
      var idx = next.indexOf(trace.name);
      if (idx >= 0) {
        next.splice(idx, 1);
      } else {
        next.push(trace.name);
      }
      return next;
    },

    updateFigureWindow: function(sliderVal, badChannels, fig, browserData) {
      if (!fig || !browserData) {
        return fig;
      }

      var nChannels = browserData.n_channels;
      var allData = browserData.all_data;
      var allDataScaled = browserData.all_data_scaled;
      var chNames = browserData.ch_names;
      var bads = new Set(Array.isArray(badChannels) ? badChannels : (browserData.bads || []));

      var maxStart = Math.max(0, chNames.length - nChannels);
      var numericSlider = Number.isFinite(sliderVal) ? sliderVal : 0;
      var channelStart = Math.max(0, Math.min(numericSlider, maxStart));

      var outFig = {
        ...fig,
        data: (fig.data || []).map(function(trace) {
          return {
            ...trace,
            line: { ...(trace.line || {}) }
          };
        }),
        layout: {
          ...fig.layout,
          yaxis: { ...((fig.layout && fig.layout.yaxis) || {}) }
        }
      };

      var blankY = Array.from({ length: browserData.times.length }, function() { return null; });
      var ticktext = [];

      for (var ii = 0; ii < nChannels; ii += 1) {
        var chIdx = channelStart + ii;
        var trace = outFig.data[ii] || { line: {} };

        if (chIdx < chNames.length) {
          var chName = chNames[chIdx];
          trace.y = allDataScaled[chIdx].map(function(v) { return v + ii; });
          trace.text = allData[chIdx];
          trace.name = chName;
          trace.line.color = bads.has(chName) ? "red" : "black";
          trace.hovertemplate =
            "<b>Channel:</b> " + chName + "<br>" +
            "<b>Time:</b> %{x:.2f} s<br>" +
            "<b>Amplitude:</b> %{text:.7f} V<br>" +
            "<extra></extra>";
          ticktext.push(chName);
        } else {
          trace.y = blankY;
          trace.text = blankY;
          trace.name = "";
          trace.line.color = "black";
          trace.hovertemplate =
            "<b>Channel:</b><br>" +
            "<b>Time:</b> %{x:.2f} s<br>" +
            "<b>Amplitude:</b> %{text:.7f} V<br>" +
            "<extra></extra>";
          ticktext.push("");
        }

        outFig.data[ii] = trace;
      }

      outFig.layout.yaxis.ticktext = ticktext;
      return outFig;
    }
  }
});
