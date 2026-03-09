(function(){
  // Lightweight enhancer for heatmap.html: adds pin toggle and delays marker layer attach
  function whenReady(fn){
    var attempts = 0;
    var iv = setInterval(function(){
      attempts++;
      if (window.map && typeof feature_group_9b76169b5aaf4ac303d71d9ce3d1f690 !== 'undefined' && typeof marker_cluster_c07d77492f872d2a1038336033860302 !== 'undefined'){
        clearInterval(iv);
        fn();
      }
      if (attempts>200) clearInterval(iv);
    },50);
  }

  function ensureToggleUI(){
    var sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
    if (document.getElementById('pinsToggle')) return; // already present
    var wrapper = document.createElement('div');
    wrapper.style.marginTop = '6px';
    wrapper.innerHTML = 'Pins: <input type="checkbox" id="pinsToggle" checked> Show pins';
    sidebar.appendChild(wrapper);
    document.getElementById('pinsToggle').addEventListener('change', function(e){
      togglePins(e.target.checked);
    });
  }

  function togglePins(show){
    try{
      if (!window.map || typeof feature_group_9b76169b5aaf4ac303d71d9ce3d1f690 === 'undefined') return;
      if (show){
        if (!map.hasLayer(feature_group_9b76169b5aaf4ac303d71d9ce3d1f690)) map.addLayer(feature_group_9b76169b5aaf4ac303d71d9ce3d1f690);
      } else {
        if (map.hasLayer(feature_group_9b76169b5aaf4ac303d71d9ce3d1f690)) map.removeLayer(feature_group_9b76169b5aaf4ac303d71d9ce3d1f690);
      }
    }catch(err){} 
  }

  whenReady(function(){
    try{
      ensureToggleUI();
      // Ensure marker_cluster is attached to feature group (it may be already)
      if (!feature_group_9b76169b5aaf4ac303d71d9ce3d1f690.hasLayer(marker_cluster_c07d77492f872d2a1038336033860302)){
        marker_cluster_c07d77492f872d2a1038336033860302.addTo(feature_group_9b76169b5aaf4ac303d71d9ce3d1f690);
      }
      // Delay adding to map slightly to avoid blocking initial render
      setTimeout(function(){
        var pinToggle = document.getElementById('pinsToggle');
        var show = pinToggle ? pinToggle.checked : true;
        if (show){
          if (!map.hasLayer(feature_group_9b76169b5aaf4ac303d71d9ce3d1f690)) map.addLayer(feature_group_9b76169b5aaf4ac303d71d9ce3d1f690);
        }
      }, 40);
    }catch(err){}    
  });

})();
