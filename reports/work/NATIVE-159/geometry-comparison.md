# Training geometry comparison — October4

Read-only comparison of900original hash-verified sidecars to qualified native159
measured boxes, same recipe IDs. No inference, training or data changes.

| Family | Count | Median old/new box area ratio | Median short edge at640 | Below3px at640 |
| --- | ---: | ---: | ---: | ---: |
| UIKitControls |700|12.1453|7.1973px|0|
| KitchenSink |200|24.2480|4.7030px|0|

Median old width/height: UIKit336×26pt, KitchenSink405×28pt. Median new width/height:
UIKit78.6667×8.3333pt, KitchenSink61×8.0833pt. Medians are coordinate-wise, not one
representative box. Short edge uses actual scale and640/max(imageWidth,imageHeight).
Area ratios computed per paired member, not ratio of median dimensions.

Implication: substantial label-target correction is established. Test corrected
geometry at the existing640input before attributing this specific failure to image
resolution. This does not establish detector improvement, adequacy for every small
control, or independent evaluation coverage. Old pixels/labels remain preserved.

Inputs: catalog e91df3c31bbc25e704ae665c0ce89c13cece9ad1ee68b0597b648ef82da2c218;
audit68a1ec913c91786df0610b693c71d1684039bfa3c71f262116833561cc269878.
