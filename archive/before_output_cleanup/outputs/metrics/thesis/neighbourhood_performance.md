# Neighbourhood Performance

Complete safe aggregate evidence; no individual source/prediction/location rows.

| city | n | r2 | mae | fold | rmse | model | scheme | pearson | train_n | spearman | estimator |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Copenhagen | 1051 | 0.2598 | 0.2803 | Amager Vest | 0.3545 | M0 | Neighbourhood | 0.6099 | 11357 | 0.6363 | OLS |
| Copenhagen | 1051 | 0.3895 | 0.2446 | Amager Vest | 0.3219 | ME | Neighbourhood | 0.6406 | 11357 | 0.6644 | OLS |
| Copenhagen | 1051 | 0.3577 | 0.2527 | Amager Vest | 0.3302 | MW | Neighbourhood | 0.6266 | 11357 | 0.6529 | OLS |
| Copenhagen | 1051 | 0.3792 | 0.2479 | Amager Vest | 0.3246 | MEW | Neighbourhood | 0.6368 | 11357 | 0.6603 | OLS |
| Copenhagen | 1051 | 0.3563 | 0.2496 | Amager Vest | 0.3306 | M0 | Neighbourhood | 0.6260 | 11357 | 0.6507 | XGBoost |
| Copenhagen | 1051 | 0.4168 | 0.2322 | Amager Vest | 0.3146 | ME | Neighbourhood | 0.6515 | 11357 | 0.6776 | XGBoost |
| Copenhagen | 1051 | 0.3840 | 0.2441 | Amager Vest | 0.3234 | MW | Neighbourhood | 0.6336 | 11357 | 0.6624 | XGBoost |
| Copenhagen | 1051 | 0.4099 | 0.2312 | Amager Vest | 0.3165 | MEW | Neighbourhood | 0.6476 | 11357 | 0.6781 | XGBoost |
| Copenhagen | 982 | 0.4324 | 0.2574 | Amager Øst | 0.3430 | M0 | Neighbourhood | 0.6731 | 11426 | 0.6885 | OLS |
| Copenhagen | 982 | 0.4893 | 0.2341 | Amager Øst | 0.3254 | ME | Neighbourhood | 0.6996 | 11426 | 0.7149 | OLS |
| Copenhagen | 982 | 0.4778 | 0.2396 | Amager Øst | 0.3290 | MW | Neighbourhood | 0.6929 | 11426 | 0.7084 | OLS |
| Copenhagen | 982 | 0.4830 | 0.2353 | Amager Øst | 0.3274 | MEW | Neighbourhood | 0.6950 | 11426 | 0.7096 | OLS |
| Copenhagen | 982 | 0.4995 | 0.2325 | Amager Øst | 0.3221 | M0 | Neighbourhood | 0.7073 | 11426 | 0.7051 | XGBoost |
| Copenhagen | 982 | 0.5159 | 0.2267 | Amager Øst | 0.3168 | ME | Neighbourhood | 0.7194 | 11426 | 0.7167 | XGBoost |
| Copenhagen | 982 | 0.5073 | 0.2303 | Amager Øst | 0.3196 | MW | Neighbourhood | 0.7128 | 11426 | 0.7102 | XGBoost |
| Copenhagen | 982 | 0.5124 | 0.2274 | Amager Øst | 0.3179 | MEW | Neighbourhood | 0.7173 | 11426 | 0.7123 | XGBoost |
| Copenhagen | 532 | 0.4000 | 0.2285 | Bispebjerg | 0.3081 | M0 | Neighbourhood | 0.6603 | 11876 | 0.6761 | OLS |
| Copenhagen | 532 | 0.4006 | 0.2286 | Bispebjerg | 0.3080 | ME | Neighbourhood | 0.6643 | 11876 | 0.6819 | OLS |
| Copenhagen | 532 | 0.4016 | 0.2274 | Bispebjerg | 0.3077 | MW | Neighbourhood | 0.6583 | 11876 | 0.6768 | OLS |
| Copenhagen | 532 | 0.3948 | 0.2301 | Bispebjerg | 0.3094 | MEW | Neighbourhood | 0.6627 | 11876 | 0.6803 | OLS |
| Copenhagen | 532 | 0.4732 | 0.2155 | Bispebjerg | 0.2887 | M0 | Neighbourhood | 0.6915 | 11876 | 0.6852 | XGBoost |
| Copenhagen | 532 | 0.4528 | 0.2224 | Bispebjerg | 0.2942 | ME | Neighbourhood | 0.6812 | 11876 | 0.6662 | XGBoost |
| Copenhagen | 532 | 0.4716 | 0.2166 | Bispebjerg | 0.2891 | MW | Neighbourhood | 0.6887 | 11876 | 0.6706 | XGBoost |
| Copenhagen | 532 | 0.4545 | 0.2225 | Bispebjerg | 0.2938 | MEW | Neighbourhood | 0.6850 | 11876 | 0.6720 | XGBoost |
| Copenhagen | 221 | 0.5246 | 0.2296 | Brønshøj-Husum | 0.2932 | M0 | Neighbourhood | 0.7569 | 12187 | 0.7675 | OLS |
| Copenhagen | 221 | 0.5190 | 0.2339 | Brønshøj-Husum | 0.2949 | ME | Neighbourhood | 0.7550 | 12187 | 0.7655 | OLS |
| Copenhagen | 221 | 0.5037 | 0.2389 | Brønshøj-Husum | 0.2996 | MW | Neighbourhood | 0.7590 | 12187 | 0.7662 | OLS |
| Copenhagen | 221 | 0.5170 | 0.2345 | Brønshøj-Husum | 0.2955 | MEW | Neighbourhood | 0.7537 | 12187 | 0.7628 | OLS |
| Copenhagen | 221 | 0.4004 | 0.2737 | Brønshøj-Husum | 0.3293 | M0 | Neighbourhood | 0.7417 | 12187 | 0.7225 | XGBoost |
| Copenhagen | 221 | 0.5082 | 0.2420 | Brønshøj-Husum | 0.2982 | ME | Neighbourhood | 0.7506 | 12187 | 0.7350 | XGBoost |
| Copenhagen | 221 | 0.4880 | 0.2462 | Brønshøj-Husum | 0.3043 | MW | Neighbourhood | 0.7473 | 12187 | 0.7270 | XGBoost |
| Copenhagen | 221 | 0.4997 | 0.2425 | Brønshøj-Husum | 0.3008 | MEW | Neighbourhood | 0.7481 | 12187 | 0.7298 | XGBoost |
| Copenhagen | 1304 | 0.4407 | 0.2299 | Frederiksberg | 0.3225 | M0 | Neighbourhood | 0.6659 | 11104 | 0.6688 | OLS |
| Copenhagen | 1304 | 0.4177 | 0.2345 | Frederiksberg | 0.3291 | ME | Neighbourhood | 0.6604 | 11104 | 0.6614 | OLS |
| Copenhagen | 1304 | 0.4239 | 0.2330 | Frederiksberg | 0.3274 | MW | Neighbourhood | 0.6655 | 11104 | 0.6673 | OLS |
| Copenhagen | 1304 | 0.4144 | 0.2351 | Frederiksberg | 0.3301 | MEW | Neighbourhood | 0.6601 | 11104 | 0.6615 | OLS |
| Copenhagen | 1304 | 0.4618 | 0.2270 | Frederiksberg | 0.3164 | M0 | Neighbourhood | 0.6835 | 11104 | 0.6746 | XGBoost |
| Copenhagen | 1304 | 0.4416 | 0.2303 | Frederiksberg | 0.3223 | ME | Neighbourhood | 0.6778 | 11104 | 0.6674 | XGBoost |
| Copenhagen | 1304 | 0.4492 | 0.2296 | Frederiksberg | 0.3201 | MW | Neighbourhood | 0.6764 | 11104 | 0.6701 | XGBoost |
| Copenhagen | 1304 | 0.4339 | 0.2319 | Frederiksberg | 0.3245 | MEW | Neighbourhood | 0.6705 | 11104 | 0.6638 | XGBoost |
| Copenhagen | 1833 | 0.2477 | 0.2936 | Indre By | 0.3927 | M0 | Neighbourhood | 0.6481 | 10575 | 0.6571 | OLS |
| Copenhagen | 1833 | 0.3501 | 0.2709 | Indre By | 0.3650 | ME | Neighbourhood | 0.6507 | 10575 | 0.6614 | OLS |
| Copenhagen | 1833 | 0.3360 | 0.2744 | Indre By | 0.3690 | MW | Neighbourhood | 0.6531 | 10575 | 0.6629 | OLS |
| Copenhagen | 1833 | 0.3423 | 0.2728 | Indre By | 0.3672 | MEW | Neighbourhood | 0.6490 | 10575 | 0.6598 | OLS |
| Copenhagen | 1833 | 0.1574 | 0.3102 | Indre By | 0.4156 | M0 | Neighbourhood | 0.6528 | 10575 | 0.6605 | XGBoost |
| Copenhagen | 1833 | 0.2472 | 0.2894 | Indre By | 0.3929 | ME | Neighbourhood | 0.6513 | 10575 | 0.6584 | XGBoost |
| Copenhagen | 1833 | 0.3046 | 0.2768 | Indre By | 0.3776 | MW | Neighbourhood | 0.6523 | 10575 | 0.6616 | XGBoost |
| Copenhagen | 1833 | 0.2888 | 0.2799 | Indre By | 0.3818 | MEW | Neighbourhood | 0.6538 | 10575 | 0.6632 | XGBoost |
| Copenhagen | 2181 | 0.3595 | 0.2147 | Nørrebro | 0.2887 | M0 | Neighbourhood | 0.6017 | 10227 | 0.5993 | OLS |
| Copenhagen | 2181 | 0.3407 | 0.2181 | Nørrebro | 0.2929 | ME | Neighbourhood | 0.5862 | 10227 | 0.5732 | OLS |
| Copenhagen | 2181 | 0.3395 | 0.2187 | Nørrebro | 0.2932 | MW | Neighbourhood | 0.5840 | 10227 | 0.5698 | OLS |
| Copenhagen | 2181 | 0.3393 | 0.2183 | Nørrebro | 0.2932 | MEW | Neighbourhood | 0.5848 | 10227 | 0.5713 | OLS |
| Copenhagen | 2181 | 0.3423 | 0.2220 | Nørrebro | 0.2926 | M0 | Neighbourhood | 0.5975 | 10227 | 0.5801 | XGBoost |
| Copenhagen | 2181 | 0.3278 | 0.2251 | Nørrebro | 0.2958 | ME | Neighbourhood | 0.5932 | 10227 | 0.5738 | XGBoost |
| Copenhagen | 2181 | 0.3233 | 0.2258 | Nørrebro | 0.2967 | MW | Neighbourhood | 0.5863 | 10227 | 0.5682 | XGBoost |
| Copenhagen | 2181 | 0.3194 | 0.2265 | Nørrebro | 0.2976 | MEW | Neighbourhood | 0.5895 | 10227 | 0.5758 | XGBoost |
| Copenhagen | 463 | 0.4610 | 0.2439 | Valby | 0.3379 | M0 | Neighbourhood | 0.6937 | 11945 | 0.7157 | OLS |
| Copenhagen | 463 | 0.4687 | 0.2390 | Valby | 0.3354 | ME | Neighbourhood | 0.6897 | 11945 | 0.7137 | OLS |
| Copenhagen | 463 | 0.4760 | 0.2362 | Valby | 0.3331 | MW | Neighbourhood | 0.6964 | 11945 | 0.7218 | OLS |
| Copenhagen | 463 | 0.4669 | 0.2395 | Valby | 0.3360 | MEW | Neighbourhood | 0.6884 | 11945 | 0.7121 | OLS |
| Copenhagen | 463 | 0.4917 | 0.2366 | Valby | 0.3281 | M0 | Neighbourhood | 0.7090 | 11945 | 0.7187 | XGBoost |
| Copenhagen | 463 | 0.4881 | 0.2380 | Valby | 0.3293 | ME | Neighbourhood | 0.7051 | 11945 | 0.7150 | XGBoost |
| Copenhagen | 463 | 0.4925 | 0.2372 | Valby | 0.3278 | MW | Neighbourhood | 0.7112 | 11945 | 0.7210 | XGBoost |
| Copenhagen | 463 | 0.4876 | 0.2380 | Valby | 0.3294 | MEW | Neighbourhood | 0.7073 | 11945 | 0.7222 | XGBoost |
| Copenhagen | 273 | 0.4148 | 0.2521 | Vanløse | 0.3413 | M0 | Neighbourhood | 0.6735 | 12135 | 0.6847 | OLS |
| Copenhagen | 273 | 0.4006 | 0.2599 | Vanløse | 0.3455 | ME | Neighbourhood | 0.6813 | 12135 | 0.6951 | OLS |
| Copenhagen | 273 | 0.4066 | 0.2565 | Vanløse | 0.3437 | MW | Neighbourhood | 0.6764 | 12135 | 0.6884 | OLS |
| Copenhagen | 273 | 0.4015 | 0.2598 | Vanløse | 0.3452 | MEW | Neighbourhood | 0.6820 | 12135 | 0.6962 | OLS |
| Copenhagen | 273 | 0.2707 | 0.2980 | Vanløse | 0.3810 | M0 | Neighbourhood | 0.6792 | 12135 | 0.7018 | XGBoost |
| Copenhagen | 273 | 0.4119 | 0.2484 | Vanløse | 0.3422 | ME | Neighbourhood | 0.6748 | 12135 | 0.6977 | XGBoost |
| Copenhagen | 273 | 0.4121 | 0.2497 | Vanløse | 0.3421 | MW | Neighbourhood | 0.6810 | 12135 | 0.7083 | XGBoost |
| Copenhagen | 273 | 0.4325 | 0.2431 | Vanløse | 0.3361 | MEW | Neighbourhood | 0.6827 | 12135 | 0.7081 | XGBoost |
| Copenhagen | 2161 | 0.3740 | 0.2343 | Vesterbro-Kongens Enghave | 0.3038 | M0 | Neighbourhood | 0.6298 | 10247 | 0.6126 | OLS |
| Copenhagen | 2161 | 0.3496 | 0.2409 | Vesterbro-Kongens Enghave | 0.3096 | ME | Neighbourhood | 0.6173 | 10247 | 0.5995 | OLS |
| Copenhagen | 2161 | 0.3384 | 0.2436 | Vesterbro-Kongens Enghave | 0.3123 | MW | Neighbourhood | 0.6150 | 10247 | 0.5966 | OLS |
| Copenhagen | 2161 | 0.3469 | 0.2417 | Vesterbro-Kongens Enghave | 0.3103 | MEW | Neighbourhood | 0.6175 | 10247 | 0.5997 | OLS |
| Copenhagen | 2161 | 0.3386 | 0.2450 | Vesterbro-Kongens Enghave | 0.3122 | M0 | Neighbourhood | 0.6503 | 10247 | 0.6292 | XGBoost |
| Copenhagen | 2161 | 0.3623 | 0.2389 | Vesterbro-Kongens Enghave | 0.3066 | ME | Neighbourhood | 0.6405 | 10247 | 0.6194 | XGBoost |
| Copenhagen | 2161 | 0.3177 | 0.2497 | Vesterbro-Kongens Enghave | 0.3171 | MW | Neighbourhood | 0.6439 | 10247 | 0.6182 | XGBoost |
| Copenhagen | 2161 | 0.3614 | 0.2393 | Vesterbro-Kongens Enghave | 0.3068 | MEW | Neighbourhood | 0.6446 | 10247 | 0.6226 | XGBoost |
| Copenhagen | 1407 | 0.2691 | 0.2611 | Østerbro | 0.3688 | M0 | Neighbourhood | 0.6035 | 11001 | 0.6028 | OLS |
| Copenhagen | 1407 | 0.3352 | 0.2498 | Østerbro | 0.3517 | ME | Neighbourhood | 0.6007 | 11001 | 0.5958 | OLS |
| Copenhagen | 1407 | 0.3184 | 0.2524 | Østerbro | 0.3561 | MW | Neighbourhood | 0.5974 | 11001 | 0.5958 | OLS |
| Copenhagen | 1407 | 0.3338 | 0.2500 | Østerbro | 0.3521 | MEW | Neighbourhood | 0.6007 | 11001 | 0.5957 | OLS |
| Copenhagen | 1407 | 0.2021 | 0.2757 | Østerbro | 0.3853 | M0 | Neighbourhood | 0.6085 | 11001 | 0.6059 | XGBoost |
| Copenhagen | 1407 | 0.2728 | 0.2612 | Østerbro | 0.3679 | ME | Neighbourhood | 0.6024 | 11001 | 0.5971 | XGBoost |
| Copenhagen | 1407 | 0.2809 | 0.2588 | Østerbro | 0.3658 | MW | Neighbourhood | 0.6168 | 11001 | 0.6154 | XGBoost |
| Copenhagen | 1407 | 0.2862 | 0.2569 | Østerbro | 0.3645 | MEW | Neighbourhood | 0.6077 | 11001 | 0.6056 | XGBoost |
| Oslo | 135 | 0.2906 | 0.2717 | Alna | 0.3708 | M0 | Neighbourhood | 0.5759 | 8394 | 0.5692 | OLS |
| Oslo | 135 | 0.3179 | 0.2656 | Alna | 0.3636 | ME | Neighbourhood | 0.5906 | 8394 | 0.5797 | OLS |
| Oslo | 135 | 0.3192 | 0.2658 | Alna | 0.3633 | MW | Neighbourhood | 0.5924 | 8394 | 0.5803 | OLS |
| Oslo | 135 | 0.3194 | 0.2634 | Alna | 0.3632 | MEW | Neighbourhood | 0.5914 | 8394 | 0.5808 | OLS |
| Oslo | 135 | 0.4312 | 0.2469 | Alna | 0.3320 | M0 | Neighbourhood | 0.6693 | 8394 | 0.6180 | XGBoost |
| Oslo | 135 | 0.4086 | 0.2550 | Alna | 0.3386 | ME | Neighbourhood | 0.6592 | 8394 | 0.6214 | XGBoost |
| Oslo | 135 | 0.4022 | 0.2555 | Alna | 0.3404 | MW | Neighbourhood | 0.6510 | 8394 | 0.6122 | XGBoost |
| Oslo | 135 | 0.4026 | 0.2558 | Alna | 0.3403 | MEW | Neighbourhood | 0.6561 | 8394 | 0.6111 | XGBoost |
| Oslo | 208 | 0.3605 | 0.2399 | Bjerke | 0.3150 | M0 | Neighbourhood | 0.6647 | 8321 | 0.6259 | OLS |
| Oslo | 208 | 0.3576 | 0.2419 | Bjerke | 0.3157 | ME | Neighbourhood | 0.6624 | 8321 | 0.6242 | OLS |
| Oslo | 208 | 0.3569 | 0.2407 | Bjerke | 0.3158 | MW | Neighbourhood | 0.6626 | 8321 | 0.6246 | OLS |
| Oslo | 208 | 0.3495 | 0.2443 | Bjerke | 0.3177 | MEW | Neighbourhood | 0.6590 | 8321 | 0.6201 | OLS |
| Oslo | 208 | 0.3890 | 0.2343 | Bjerke | 0.3079 | M0 | Neighbourhood | 0.6601 | 8321 | 0.6360 | XGBoost |
| Oslo | 208 | 0.3830 | 0.2370 | Bjerke | 0.3094 | ME | Neighbourhood | 0.6642 | 8321 | 0.6372 | XGBoost |
| Oslo | 208 | 0.3566 | 0.2419 | Bjerke | 0.3159 | MW | Neighbourhood | 0.6532 | 8321 | 0.6290 | XGBoost |
| Oslo | 208 | 0.3642 | 0.2417 | Bjerke | 0.3140 | MEW | Neighbourhood | 0.6601 | 8321 | 0.6337 | XGBoost |
| Oslo | 1257 | 0.3890 | 0.2866 | Frogner | 0.4045 | M0 | Neighbourhood | 0.6372 | 7272 | 0.6593 | OLS |
| Oslo | 1257 | 0.3936 | 0.2855 | Frogner | 0.4029 | ME | Neighbourhood | 0.6437 | 7272 | 0.6672 | OLS |
| Oslo | 1257 | 0.3915 | 0.2859 | Frogner | 0.4036 | MW | Neighbourhood | 0.6415 | 7272 | 0.6639 | OLS |
| Oslo | 1257 | 0.3950 | 0.2855 | Frogner | 0.4025 | MEW | Neighbourhood | 0.6428 | 7272 | 0.6660 | OLS |
| Oslo | 1257 | 0.4181 | 0.2789 | Frogner | 0.3947 | M0 | Neighbourhood | 0.6672 | 7272 | 0.6665 | XGBoost |
| Oslo | 1257 | 0.4305 | 0.2773 | Frogner | 0.3905 | ME | Neighbourhood | 0.6668 | 7272 | 0.6679 | XGBoost |
| Oslo | 1257 | 0.4234 | 0.2771 | Frogner | 0.3929 | MW | Neighbourhood | 0.6698 | 7272 | 0.6717 | XGBoost |
| Oslo | 1257 | 0.4210 | 0.2785 | Frogner | 0.3937 | MEW | Neighbourhood | 0.6670 | 7272 | 0.6710 | XGBoost |
| Oslo | 1542 | 0.4396 | 0.2707 | Gamle Oslo | 0.3781 | M0 | Neighbourhood | 0.6683 | 6987 | 0.7050 | OLS |
| Oslo | 1542 | 0.4504 | 0.2675 | Gamle Oslo | 0.3745 | ME | Neighbourhood | 0.6764 | 6987 | 0.7117 | OLS |
| Oslo | 1542 | 0.4429 | 0.2695 | Gamle Oslo | 0.3770 | MW | Neighbourhood | 0.6708 | 6987 | 0.7067 | OLS |
| Oslo | 1542 | 0.4430 | 0.2690 | Gamle Oslo | 0.3770 | MEW | Neighbourhood | 0.6714 | 6987 | 0.7065 | OLS |
| Oslo | 1542 | 0.4833 | 0.2588 | Gamle Oslo | 0.3631 | M0 | Neighbourhood | 0.6994 | 6987 | 0.7059 | XGBoost |
| Oslo | 1542 | 0.4775 | 0.2608 | Gamle Oslo | 0.3651 | ME | Neighbourhood | 0.6939 | 6987 | 0.7083 | XGBoost |
| Oslo | 1542 | 0.4838 | 0.2601 | Gamle Oslo | 0.3629 | MW | Neighbourhood | 0.6976 | 6987 | 0.7057 | XGBoost |
| Oslo | 1542 | 0.4752 | 0.2607 | Gamle Oslo | 0.3659 | MEW | Neighbourhood | 0.6934 | 6987 | 0.7084 | XGBoost |
| Oslo | 51 | 0.5406 | 0.2185 | Grorud | 0.2984 | M0 | Neighbourhood | 0.7549 | 8478 | 0.7100 | OLS |
| Oslo | 51 | 0.5380 | 0.2191 | Grorud | 0.2992 | ME | Neighbourhood | 0.7574 | 8478 | 0.7220 | OLS |
| Oslo | 51 | 0.5224 | 0.2261 | Grorud | 0.3043 | MW | Neighbourhood | 0.7538 | 8478 | 0.7086 | OLS |
| Oslo | 51 | 0.5560 | 0.2179 | Grorud | 0.2934 | MEW | Neighbourhood | 0.7628 | 8478 | 0.7146 | OLS |
| Oslo | 51 | 0.4302 | 0.2569 | Grorud | 0.3323 | M0 | Neighbourhood | 0.7739 | 8478 | 0.7283 | XGBoost |
| Oslo | 51 | 0.4428 | 0.2611 | Grorud | 0.3286 | ME | Neighbourhood | 0.7692 | 8478 | 0.7269 | XGBoost |
| Oslo | 51 | 0.4584 | 0.2515 | Grorud | 0.3240 | MW | Neighbourhood | 0.7890 | 8478 | 0.7269 | XGBoost |
| Oslo | 51 | 0.4275 | 0.2645 | Grorud | 0.3331 | MEW | Neighbourhood | 0.7741 | 8478 | 0.7336 | XGBoost |
| Oslo | 1589 | 0.4556 | 0.2246 | Grünerløkka | 0.3078 | M0 | Neighbourhood | 0.6754 | 6940 | 0.6901 | OLS |
| Oslo | 1589 | 0.4511 | 0.2263 | Grünerløkka | 0.3090 | ME | Neighbourhood | 0.6718 | 6940 | 0.6865 | OLS |
| Oslo | 1589 | 0.4533 | 0.2256 | Grünerløkka | 0.3084 | MW | Neighbourhood | 0.6736 | 6940 | 0.6886 | OLS |
| Oslo | 1589 | 0.4517 | 0.2266 | Grünerløkka | 0.3089 | MEW | Neighbourhood | 0.6725 | 6940 | 0.6875 | OLS |
| Oslo | 1589 | 0.4746 | 0.2180 | Grünerløkka | 0.3023 | M0 | Neighbourhood | 0.6926 | 6940 | 0.7103 | XGBoost |
| Oslo | 1589 | 0.4721 | 0.2183 | Grünerløkka | 0.3031 | ME | Neighbourhood | 0.6883 | 6940 | 0.7076 | XGBoost |
| Oslo | 1589 | 0.4686 | 0.2203 | Grünerløkka | 0.3041 | MW | Neighbourhood | 0.6871 | 6940 | 0.7048 | XGBoost |
| Oslo | 1589 | 0.4691 | 0.2198 | Grünerløkka | 0.3039 | MEW | Neighbourhood | 0.6862 | 6940 | 0.7065 | XGBoost |
| Oslo | 32 | -0.1127 | 0.4009 | Marka | 0.5182 | M0 | Neighbourhood | 0.5736 | 8497 | 0.5359 | OLS |
| Oslo | 32 | -0.6368 | 0.5250 | Marka | 0.6285 | ME | Neighbourhood | 0.5554 | 8497 | 0.5499 | OLS |
| Oslo | 32 | -0.7424 | 0.5474 | Marka | 0.6485 | MW | Neighbourhood | 0.5691 | 8497 | 0.5627 | OLS |
| Oslo | 32 | -0.7101 | 0.5360 | Marka | 0.6424 | MEW | Neighbourhood | 0.5565 | 8497 | 0.5422 | OLS |
| Oslo | 32 | 0.3236 | 0.3138 | Marka | 0.4040 | M0 | Neighbourhood | 0.5988 | 8497 | 0.5037 | XGBoost |
| Oslo | 32 | 0.2179 | 0.3321 | Marka | 0.4344 | ME | Neighbourhood | 0.5897 | 8497 | 0.5092 | XGBoost |
| Oslo | 32 | 0.2185 | 0.3363 | Marka | 0.4343 | MW | Neighbourhood | 0.5455 | 8497 | 0.4311 | XGBoost |
| Oslo | 32 | 0.3099 | 0.3149 | Marka | 0.4081 | MEW | Neighbourhood | 0.5951 | 8497 | 0.4956 | XGBoost |
| Oslo | 359 | 0.5889 | 0.2662 | Nordre Aker | 0.3486 | M0 | Neighbourhood | 0.7845 | 8170 | 0.8021 | OLS |
| Oslo | 359 | 0.5935 | 0.2634 | Nordre Aker | 0.3467 | ME | Neighbourhood | 0.7839 | 8170 | 0.8011 | OLS |
| Oslo | 359 | 0.5965 | 0.2639 | Nordre Aker | 0.3454 | MW | Neighbourhood | 0.7862 | 8170 | 0.8053 | OLS |
| Oslo | 359 | 0.5949 | 0.2632 | Nordre Aker | 0.3460 | MEW | Neighbourhood | 0.7830 | 8170 | 0.7991 | OLS |
| Oslo | 359 | 0.6595 | 0.2435 | Nordre Aker | 0.3173 | M0 | Neighbourhood | 0.8158 | 8170 | 0.8146 | XGBoost |
| Oslo | 359 | 0.6574 | 0.2421 | Nordre Aker | 0.3182 | ME | Neighbourhood | 0.8127 | 8170 | 0.8182 | XGBoost |
| Oslo | 359 | 0.6576 | 0.2451 | Nordre Aker | 0.3181 | MW | Neighbourhood | 0.8166 | 8170 | 0.8176 | XGBoost |
| Oslo | 359 | 0.6569 | 0.2435 | Nordre Aker | 0.3185 | MEW | Neighbourhood | 0.8132 | 8170 | 0.8164 | XGBoost |
| Oslo | 431 | 0.5862 | 0.2943 | Nordstrand | 0.3816 | M0 | Neighbourhood | 0.7958 | 8098 | 0.8215 | OLS |
| Oslo | 431 | 0.5900 | 0.2928 | Nordstrand | 0.3799 | ME | Neighbourhood | 0.7963 | 8098 | 0.8210 | OLS |
| Oslo | 431 | 0.5847 | 0.2948 | Nordstrand | 0.3823 | MW | Neighbourhood | 0.7942 | 8098 | 0.8182 | OLS |
| Oslo | 431 | 0.5943 | 0.2907 | Nordstrand | 0.3779 | MEW | Neighbourhood | 0.7976 | 8098 | 0.8205 | OLS |
| Oslo | 431 | 0.4994 | 0.3260 | Nordstrand | 0.4198 | M0 | Neighbourhood | 0.7966 | 8098 | 0.8202 | XGBoost |
| Oslo | 431 | 0.5263 | 0.3120 | Nordstrand | 0.4084 | ME | Neighbourhood | 0.7861 | 8098 | 0.8077 | XGBoost |
| Oslo | 431 | 0.5340 | 0.3124 | Nordstrand | 0.4050 | MW | Neighbourhood | 0.7959 | 8098 | 0.8146 | XGBoost |
| Oslo | 431 | 0.5193 | 0.3173 | Nordstrand | 0.4113 | MEW | Neighbourhood | 0.7782 | 8098 | 0.8033 | XGBoost |
| Oslo | 932 | 0.3516 | 0.2227 | Sagene | 0.3065 | M0 | Neighbourhood | 0.5958 | 7597 | 0.5999 | OLS |
| Oslo | 932 | 0.3332 | 0.2293 | Sagene | 0.3108 | ME | Neighbourhood | 0.5837 | 7597 | 0.5875 | OLS |
| Oslo | 932 | 0.3403 | 0.2276 | Sagene | 0.3092 | MW | Neighbourhood | 0.5890 | 7597 | 0.5921 | OLS |
| Oslo | 932 | 0.3294 | 0.2309 | Sagene | 0.3117 | MEW | Neighbourhood | 0.5821 | 7597 | 0.5861 | OLS |
| Oslo | 932 | 0.3873 | 0.2183 | Sagene | 0.2980 | M0 | Neighbourhood | 0.6235 | 7597 | 0.6009 | XGBoost |
| Oslo | 932 | 0.3763 | 0.2221 | Sagene | 0.3006 | ME | Neighbourhood | 0.6222 | 7597 | 0.6026 | XGBoost |
| Oslo | 932 | 0.3783 | 0.2225 | Sagene | 0.3002 | MW | Neighbourhood | 0.6268 | 7597 | 0.6083 | XGBoost |
| Oslo | 932 | 0.3712 | 0.2238 | Sagene | 0.3019 | MEW | Neighbourhood | 0.6218 | 7597 | 0.6021 | XGBoost |
| Oslo | 147 | 0.2867 | 0.2647 | Sentrum | 0.3509 | M0 | Neighbourhood | 0.5673 | 8382 | 0.5365 | OLS |
| Oslo | 147 | 0.2923 | 0.2633 | Sentrum | 0.3495 | ME | Neighbourhood | 0.5697 | 8382 | 0.5389 | OLS |
| Oslo | 147 | 0.2846 | 0.2657 | Sentrum | 0.3514 | MW | Neighbourhood | 0.5689 | 8382 | 0.5379 | OLS |
| Oslo | 147 | 0.2855 | 0.2656 | Sentrum | 0.3512 | MEW | Neighbourhood | 0.5679 | 8382 | 0.5380 | OLS |
| Oslo | 147 | 0.3261 | 0.2644 | Sentrum | 0.3411 | M0 | Neighbourhood | 0.6165 | 8382 | 0.5596 | XGBoost |
| Oslo | 147 | 0.3715 | 0.2414 | Sentrum | 0.3294 | ME | Neighbourhood | 0.6270 | 8382 | 0.5486 | XGBoost |
| Oslo | 147 | 0.3858 | 0.2411 | Sentrum | 0.3256 | MW | Neighbourhood | 0.6237 | 8382 | 0.5685 | XGBoost |
| Oslo | 147 | 0.3415 | 0.2475 | Sentrum | 0.3372 | MEW | Neighbourhood | 0.6073 | 8382 | 0.5261 | XGBoost |
| Oslo | 985 | 0.4663 | 0.2630 | St. Hanshaugen | 0.3429 | M0 | Neighbourhood | 0.6962 | 7544 | 0.6700 | OLS |
| Oslo | 985 | 0.4646 | 0.2631 | St. Hanshaugen | 0.3434 | ME | Neighbourhood | 0.6931 | 7544 | 0.6683 | OLS |
| Oslo | 985 | 0.4590 | 0.2651 | St. Hanshaugen | 0.3452 | MW | Neighbourhood | 0.6912 | 7544 | 0.6662 | OLS |
| Oslo | 985 | 0.4648 | 0.2631 | St. Hanshaugen | 0.3433 | MEW | Neighbourhood | 0.6918 | 7544 | 0.6681 | OLS |
| Oslo | 985 | 0.5289 | 0.2513 | St. Hanshaugen | 0.3221 | M0 | Neighbourhood | 0.7445 | 7544 | 0.7030 | XGBoost |
| Oslo | 985 | 0.4885 | 0.2617 | St. Hanshaugen | 0.3356 | ME | Neighbourhood | 0.7264 | 7544 | 0.6914 | XGBoost |
| Oslo | 985 | 0.4866 | 0.2625 | St. Hanshaugen | 0.3363 | MW | Neighbourhood | 0.7212 | 7544 | 0.6932 | XGBoost |
| Oslo | 985 | 0.4819 | 0.2641 | St. Hanshaugen | 0.3378 | MEW | Neighbourhood | 0.7173 | 7544 | 0.6853 | XGBoost |
| Oslo | 33 | 0.5679 | 0.2913 | Stovner | 0.3905 | M0 | Neighbourhood | 0.8419 | 8496 | 0.7440 | OLS |
| Oslo | 33 | 0.5765 | 0.2813 | Stovner | 0.3866 | ME | Neighbourhood | 0.8381 | 8496 | 0.7370 | OLS |
| Oslo | 33 | 0.5946 | 0.2775 | Stovner | 0.3783 | MW | Neighbourhood | 0.8389 | 8496 | 0.7380 | OLS |
| Oslo | 33 | 0.5870 | 0.2735 | Stovner | 0.3818 | MEW | Neighbourhood | 0.8428 | 8496 | 0.7430 | OLS |
| Oslo | 33 | 0.6597 | 0.2343 | Stovner | 0.3465 | M0 | Neighbourhood | 0.8179 | 8496 | 0.7543 | XGBoost |
| Oslo | 33 | 0.6939 | 0.2293 | Stovner | 0.3287 | ME | Neighbourhood | 0.8346 | 8496 | 0.7263 | XGBoost |
| Oslo | 33 | 0.6945 | 0.2318 | Stovner | 0.3284 | MW | Neighbourhood | 0.8363 | 8496 | 0.7403 | XGBoost |
| Oslo | 33 | 0.7018 | 0.2276 | Stovner | 0.3244 | MEW | Neighbourhood | 0.8407 | 8496 | 0.7159 | XGBoost |
| Oslo | 82 | 0.4243 | 0.2514 | Søndre Nordstrand | 0.3507 | M0 | Neighbourhood | 0.6776 | 8447 | 0.7059 | OLS |
| Oslo | 82 | 0.4521 | 0.2503 | Søndre Nordstrand | 0.3422 | ME | Neighbourhood | 0.6856 | 8447 | 0.7102 | OLS |
| Oslo | 82 | 0.4427 | 0.2542 | Søndre Nordstrand | 0.3451 | MW | Neighbourhood | 0.6808 | 8447 | 0.7085 | OLS |
| Oslo | 82 | 0.4481 | 0.2526 | Søndre Nordstrand | 0.3434 | MEW | Neighbourhood | 0.6828 | 8447 | 0.6974 | OLS |
| Oslo | 82 | 0.3043 | 0.3095 | Søndre Nordstrand | 0.3855 | M0 | Neighbourhood | 0.7037 | 8447 | 0.7156 | XGBoost |
| Oslo | 82 | 0.2993 | 0.3145 | Søndre Nordstrand | 0.3869 | ME | Neighbourhood | 0.6936 | 8447 | 0.7072 | XGBoost |
| Oslo | 82 | 0.2434 | 0.3251 | Søndre Nordstrand | 0.4021 | MW | Neighbourhood | 0.6922 | 8447 | 0.7050 | XGBoost |
| Oslo | 82 | 0.2466 | 0.3242 | Søndre Nordstrand | 0.4012 | MEW | Neighbourhood | 0.6832 | 8447 | 0.6950 | XGBoost |
| Oslo | 248 | 0.3545 | 0.2756 | Ullern | 0.4065 | M0 | Neighbourhood | 0.6470 | 8281 | 0.7206 | OLS |
| Oslo | 248 | 0.3482 | 0.2781 | Ullern | 0.4084 | ME | Neighbourhood | 0.6437 | 8281 | 0.7172 | OLS |
| Oslo | 248 | 0.3605 | 0.2743 | Ullern | 0.4046 | MW | Neighbourhood | 0.6482 | 8281 | 0.7227 | OLS |
| Oslo | 248 | 0.3454 | 0.2798 | Ullern | 0.4093 | MEW | Neighbourhood | 0.6412 | 8281 | 0.7123 | OLS |
| Oslo | 248 | 0.4147 | 0.2670 | Ullern | 0.3871 | M0 | Neighbourhood | 0.6797 | 8281 | 0.7374 | XGBoost |
| Oslo | 248 | 0.4004 | 0.2680 | Ullern | 0.3917 | ME | Neighbourhood | 0.6670 | 8281 | 0.7299 | XGBoost |
| Oslo | 248 | 0.4035 | 0.2660 | Ullern | 0.3908 | MW | Neighbourhood | 0.6709 | 8281 | 0.7319 | XGBoost |
| Oslo | 248 | 0.3918 | 0.2701 | Ullern | 0.3946 | MEW | Neighbourhood | 0.6617 | 8281 | 0.7240 | XGBoost |
| Oslo | 263 | 0.6072 | 0.2837 | Vestre Aker | 0.3921 | M0 | Neighbourhood | 0.7820 | 8266 | 0.7942 | OLS |
| Oslo | 263 | 0.6046 | 0.2851 | Vestre Aker | 0.3934 | ME | Neighbourhood | 0.7803 | 8266 | 0.7903 | OLS |
| Oslo | 263 | 0.6057 | 0.2848 | Vestre Aker | 0.3929 | MW | Neighbourhood | 0.7818 | 8266 | 0.7933 | OLS |
| Oslo | 263 | 0.6041 | 0.2839 | Vestre Aker | 0.3937 | MEW | Neighbourhood | 0.7800 | 8266 | 0.7898 | OLS |
| Oslo | 263 | 0.5871 | 0.2961 | Vestre Aker | 0.4020 | M0 | Neighbourhood | 0.7728 | 8266 | 0.8090 | XGBoost |
| Oslo | 263 | 0.5946 | 0.2915 | Vestre Aker | 0.3983 | ME | Neighbourhood | 0.7749 | 8266 | 0.8142 | XGBoost |
| Oslo | 263 | 0.5927 | 0.2940 | Vestre Aker | 0.3993 | MW | Neighbourhood | 0.7766 | 8266 | 0.8146 | XGBoost |
| Oslo | 263 | 0.5978 | 0.2916 | Vestre Aker | 0.3968 | MEW | Neighbourhood | 0.7763 | 8266 | 0.8166 | XGBoost |
| Oslo | 235 | 0.3121 | 0.2828 | Østensjø | 0.4337 | M0 | Neighbourhood | 0.5967 | 8294 | 0.7011 | OLS |
| Oslo | 235 | 0.3063 | 0.2834 | Østensjø | 0.4355 | ME | Neighbourhood | 0.5927 | 8294 | 0.6950 | OLS |
| Oslo | 235 | 0.3099 | 0.2819 | Østensjø | 0.4344 | MW | Neighbourhood | 0.5936 | 8294 | 0.6981 | OLS |
| Oslo | 235 | 0.3055 | 0.2856 | Østensjø | 0.4358 | MEW | Neighbourhood | 0.5923 | 8294 | 0.6951 | OLS |
| Oslo | 235 | 0.3487 | 0.2736 | Østensjø | 0.4220 | M0 | Neighbourhood | 0.6060 | 8294 | 0.7092 | XGBoost |
| Oslo | 235 | 0.3686 | 0.2680 | Østensjø | 0.4155 | ME | Neighbourhood | 0.6167 | 8294 | 0.7179 | XGBoost |
| Oslo | 235 | 0.3703 | 0.2679 | Østensjø | 0.4149 | MW | Neighbourhood | 0.6170 | 8294 | 0.7219 | XGBoost |
| Oslo | 235 | 0.3702 | 0.2667 | Østensjø | 0.4150 | MEW | Neighbourhood | 0.6168 | 8294 | 0.7203 | XGBoost |
| Stockholm | 170 | 0.6932 | 0.2633 | Bromma | 0.3402 | M0 | Neighbourhood | 0.8486 | 2325 | 0.8542 | OLS |
| Stockholm | 170 | 0.6730 | 0.2729 | Bromma | 0.3512 | ME | Neighbourhood | 0.8419 | 2325 | 0.8427 | OLS |
| Stockholm | 170 | 0.6737 | 0.2729 | Bromma | 0.3508 | MW | Neighbourhood | 0.8400 | 2325 | 0.8364 | OLS |
| Stockholm | 170 | 0.6785 | 0.2715 | Bromma | 0.3482 | MEW | Neighbourhood | 0.8411 | 2325 | 0.8390 | OLS |
| Stockholm | 170 | 0.7085 | 0.2591 | Bromma | 0.3316 | M0 | Neighbourhood | 0.8598 | 2325 | 0.8565 | XGBoost |
| Stockholm | 170 | 0.7085 | 0.2596 | Bromma | 0.3316 | ME | Neighbourhood | 0.8663 | 2325 | 0.8588 | XGBoost |
| Stockholm | 170 | 0.6777 | 0.2699 | Bromma | 0.3487 | MW | Neighbourhood | 0.8510 | 2325 | 0.8399 | XGBoost |
| Stockholm | 170 | 0.6862 | 0.2709 | Bromma | 0.3440 | MEW | Neighbourhood | 0.8549 | 2325 | 0.8490 | XGBoost |
| Stockholm | 220 | 0.6032 | 0.3472 | Enskede-Årsta-Vantör | 0.4663 | M0 | Neighbourhood | 0.8135 | 2275 | 0.8163 | OLS |
| Stockholm | 220 | 0.6458 | 0.3353 | Enskede-Årsta-Vantör | 0.4405 | ME | Neighbourhood | 0.8130 | 2275 | 0.8153 | OLS |
| Stockholm | 220 | 0.6422 | 0.3366 | Enskede-Årsta-Vantör | 0.4428 | MW | Neighbourhood | 0.8121 | 2275 | 0.8141 | OLS |
| Stockholm | 220 | 0.6397 | 0.3378 | Enskede-Årsta-Vantör | 0.4443 | MEW | Neighbourhood | 0.8112 | 2275 | 0.8127 | OLS |
| Stockholm | 220 | 0.7186 | 0.2962 | Enskede-Årsta-Vantör | 0.3926 | M0 | Neighbourhood | 0.8517 | 2275 | 0.8358 | XGBoost |
| Stockholm | 220 | 0.7036 | 0.3040 | Enskede-Årsta-Vantör | 0.4030 | ME | Neighbourhood | 0.8430 | 2275 | 0.8294 | XGBoost |
| Stockholm | 220 | 0.7034 | 0.3078 | Enskede-Årsta-Vantör | 0.4031 | MW | Neighbourhood | 0.8418 | 2275 | 0.8291 | XGBoost |
| Stockholm | 220 | 0.6976 | 0.3104 | Enskede-Årsta-Vantör | 0.4070 | MEW | Neighbourhood | 0.8397 | 2275 | 0.8275 | XGBoost |
| Stockholm | 100 | 0.5839 | 0.3086 | Farsta | 0.4027 | M0 | Neighbourhood | 0.7699 | 2395 | 0.7258 | OLS |
| Stockholm | 100 | 0.5774 | 0.3034 | Farsta | 0.4058 | ME | Neighbourhood | 0.7672 | 2395 | 0.7025 | OLS |
| Stockholm | 100 | 0.5899 | 0.2990 | Farsta | 0.3998 | MW | Neighbourhood | 0.7758 | 2395 | 0.7221 | OLS |
| Stockholm | 100 | 0.5837 | 0.3001 | Farsta | 0.4028 | MEW | Neighbourhood | 0.7710 | 2395 | 0.7061 | OLS |
| Stockholm | 100 | 0.6139 | 0.2930 | Farsta | 0.3879 | M0 | Neighbourhood | 0.7912 | 2395 | 0.7114 | XGBoost |
| Stockholm | 100 | 0.6008 | 0.2871 | Farsta | 0.3944 | ME | Neighbourhood | 0.7814 | 2395 | 0.7052 | XGBoost |
| Stockholm | 100 | 0.6169 | 0.2894 | Farsta | 0.3864 | MW | Neighbourhood | 0.7922 | 2395 | 0.7110 | XGBoost |
| Stockholm | 100 | 0.6163 | 0.2878 | Farsta | 0.3867 | MEW | Neighbourhood | 0.7895 | 2395 | 0.7132 | XGBoost |
| Stockholm | 343 | 0.5443 | 0.3187 | Hägersten-Älvsjö | 0.4268 | M0 | Neighbourhood | 0.7737 | 2152 | 0.7995 | OLS |
| Stockholm | 343 | 0.5791 | 0.3047 | Hägersten-Älvsjö | 0.4102 | ME | Neighbourhood | 0.7755 | 2152 | 0.7985 | OLS |
| Stockholm | 343 | 0.5747 | 0.3092 | Hägersten-Älvsjö | 0.4123 | MW | Neighbourhood | 0.7744 | 2152 | 0.7987 | OLS |
| Stockholm | 343 | 0.5827 | 0.3047 | Hägersten-Älvsjö | 0.4084 | MEW | Neighbourhood | 0.7753 | 2152 | 0.7978 | OLS |
| Stockholm | 343 | 0.5734 | 0.3173 | Hägersten-Älvsjö | 0.4130 | M0 | Neighbourhood | 0.8041 | 2152 | 0.8010 | XGBoost |
| Stockholm | 343 | 0.6095 | 0.3047 | Hägersten-Älvsjö | 0.3951 | ME | Neighbourhood | 0.7965 | 2152 | 0.7889 | XGBoost |
| Stockholm | 343 | 0.6195 | 0.3009 | Hägersten-Älvsjö | 0.3900 | MW | Neighbourhood | 0.8027 | 2152 | 0.7926 | XGBoost |
| Stockholm | 343 | 0.6199 | 0.2989 | Hägersten-Älvsjö | 0.3898 | MEW | Neighbourhood | 0.8014 | 2152 | 0.7918 | XGBoost |
| Stockholm | 81 | 0.5074 | 0.3959 | Hässelby-Vällingby | 0.4917 | M0 | Neighbourhood | 0.7716 | 2414 | 0.8031 | OLS |
| Stockholm | 81 | 0.5958 | 0.3488 | Hässelby-Vällingby | 0.4454 | ME | Neighbourhood | 0.7823 | 2414 | 0.8048 | OLS |
| Stockholm | 81 | 0.5930 | 0.3490 | Hässelby-Vällingby | 0.4470 | MW | Neighbourhood | 0.7801 | 2414 | 0.8108 | OLS |
| Stockholm | 81 | 0.6049 | 0.3435 | Hässelby-Vällingby | 0.4404 | MEW | Neighbourhood | 0.7884 | 2414 | 0.8146 | OLS |
| Stockholm | 81 | 0.5505 | 0.3849 | Hässelby-Vällingby | 0.4698 | M0 | Neighbourhood | 0.8532 | 2414 | 0.8441 | XGBoost |
| Stockholm | 81 | 0.4988 | 0.4174 | Hässelby-Vällingby | 0.4961 | ME | Neighbourhood | 0.8349 | 2414 | 0.8185 | XGBoost |
| Stockholm | 81 | 0.5524 | 0.3817 | Hässelby-Vällingby | 0.4687 | MW | Neighbourhood | 0.8456 | 2414 | 0.8384 | XGBoost |
| Stockholm | 81 | 0.5405 | 0.3895 | Hässelby-Vällingby | 0.4750 | MEW | Neighbourhood | 0.8418 | 2414 | 0.8270 | XGBoost |
| Stockholm | 91 | 0.7320 | 0.3213 | Järva | 0.4112 | M0 | Neighbourhood | 0.8607 | 2404 | 0.8621 | OLS |
| Stockholm | 91 | 0.7346 | 0.3239 | Järva | 0.4092 | ME | Neighbourhood | 0.8578 | 2404 | 0.8647 | OLS |
| Stockholm | 91 | 0.7449 | 0.3151 | Järva | 0.4012 | MW | Neighbourhood | 0.8655 | 2404 | 0.8742 | OLS |
| Stockholm | 91 | 0.7406 | 0.3235 | Järva | 0.4045 | MEW | Neighbourhood | 0.8616 | 2404 | 0.8683 | OLS |
| Stockholm | 91 | 0.7901 | 0.2825 | Järva | 0.3638 | M0 | Neighbourhood | 0.8920 | 2404 | 0.9009 | XGBoost |
| Stockholm | 91 | 0.7907 | 0.2847 | Järva | 0.3633 | ME | Neighbourhood | 0.8935 | 2404 | 0.8859 | XGBoost |
| Stockholm | 91 | 0.7871 | 0.2899 | Järva | 0.3664 | MW | Neighbourhood | 0.8917 | 2404 | 0.8885 | XGBoost |
| Stockholm | 91 | 0.7838 | 0.2968 | Järva | 0.3693 | MEW | Neighbourhood | 0.8922 | 2404 | 0.8852 | XGBoost |
| Stockholm | 235 | 0.4311 | 0.3052 | Kungsholmen | 0.4071 | M0 | Neighbourhood | 0.7002 | 2260 | 0.7052 | OLS |
| Stockholm | 235 | 0.4899 | 0.2810 | Kungsholmen | 0.3855 | ME | Neighbourhood | 0.7028 | 2260 | 0.7078 | OLS |
| Stockholm | 235 | 0.5057 | 0.2777 | Kungsholmen | 0.3795 | MW | Neighbourhood | 0.7119 | 2260 | 0.7185 | OLS |
| Stockholm | 235 | 0.4977 | 0.2792 | Kungsholmen | 0.3826 | MEW | Neighbourhood | 0.7062 | 2260 | 0.7145 | OLS |
| Stockholm | 235 | 0.4810 | 0.3046 | Kungsholmen | 0.3889 | M0 | Neighbourhood | 0.7190 | 2260 | 0.7219 | XGBoost |
| Stockholm | 235 | 0.5093 | 0.2872 | Kungsholmen | 0.3781 | ME | Neighbourhood | 0.7223 | 2260 | 0.7340 | XGBoost |
| Stockholm | 235 | 0.5286 | 0.2870 | Kungsholmen | 0.3706 | MW | Neighbourhood | 0.7309 | 2260 | 0.7388 | XGBoost |
| Stockholm | 235 | 0.5151 | 0.2847 | Kungsholmen | 0.3759 | MEW | Neighbourhood | 0.7249 | 2260 | 0.7381 | XGBoost |
| Stockholm | 423 | 0.3875 | 0.3583 | Norra innerstaden | 0.4843 | M0 | Neighbourhood | 0.7422 | 2072 | 0.7095 | OLS |
| Stockholm | 423 | 0.4998 | 0.3200 | Norra innerstaden | 0.4377 | ME | Neighbourhood | 0.7437 | 2072 | 0.7116 | OLS |
| Stockholm | 423 | 0.4854 | 0.3248 | Norra innerstaden | 0.4439 | MW | Neighbourhood | 0.7438 | 2072 | 0.7120 | OLS |
| Stockholm | 423 | 0.4982 | 0.3201 | Norra innerstaden | 0.4383 | MEW | Neighbourhood | 0.7393 | 2072 | 0.7071 | OLS |
| Stockholm | 423 | 0.4661 | 0.3324 | Norra innerstaden | 0.4521 | M0 | Neighbourhood | 0.7884 | 2072 | 0.7578 | XGBoost |
| Stockholm | 423 | 0.5686 | 0.2954 | Norra innerstaden | 0.4064 | ME | Neighbourhood | 0.7667 | 2072 | 0.7219 | XGBoost |
| Stockholm | 423 | 0.5784 | 0.2942 | Norra innerstaden | 0.4018 | MW | Neighbourhood | 0.7840 | 2072 | 0.7476 | XGBoost |
| Stockholm | 423 | 0.5744 | 0.2944 | Norra innerstaden | 0.4037 | MEW | Neighbourhood | 0.7662 | 2072 | 0.7204 | XGBoost |
| Stockholm | 99 | 0.5830 | 0.2970 | Skarpnäck | 0.4936 | M0 | Neighbourhood | 0.7740 | 2396 | 0.8253 | OLS |
| Stockholm | 99 | 0.5861 | 0.3050 | Skarpnäck | 0.4918 | ME | Neighbourhood | 0.7710 | 2396 | 0.8209 | OLS |
| Stockholm | 99 | 0.5850 | 0.3026 | Skarpnäck | 0.4924 | MW | Neighbourhood | 0.7722 | 2396 | 0.8235 | OLS |
| Stockholm | 99 | 0.5904 | 0.3016 | Skarpnäck | 0.4892 | MEW | Neighbourhood | 0.7717 | 2396 | 0.8299 | OLS |
| Stockholm | 99 | 0.6129 | 0.3001 | Skarpnäck | 0.4756 | M0 | Neighbourhood | 0.8108 | 2396 | 0.8262 | XGBoost |
| Stockholm | 99 | 0.6305 | 0.2999 | Skarpnäck | 0.4647 | ME | Neighbourhood | 0.8109 | 2396 | 0.8220 | XGBoost |
| Stockholm | 99 | 0.6288 | 0.2891 | Skarpnäck | 0.4657 | MW | Neighbourhood | 0.8077 | 2396 | 0.8328 | XGBoost |
| Stockholm | 99 | 0.6244 | 0.2927 | Skarpnäck | 0.4685 | MEW | Neighbourhood | 0.7994 | 2396 | 0.8281 | XGBoost |
| Stockholm | 38 | 0.5053 | 0.3827 | Skärholmen | 0.5244 | M0 | Neighbourhood | 0.7197 | 2457 | 0.7125 | OLS |
| Stockholm | 38 | 0.4781 | 0.3863 | Skärholmen | 0.5386 | ME | Neighbourhood | 0.7088 | 2457 | 0.6667 | OLS |
| Stockholm | 38 | 0.4626 | 0.4048 | Skärholmen | 0.5466 | MW | Neighbourhood | 0.6990 | 2457 | 0.6746 | OLS |
| Stockholm | 38 | 0.4711 | 0.3977 | Skärholmen | 0.5422 | MEW | Neighbourhood | 0.7116 | 2457 | 0.6892 | OLS |
| Stockholm | 38 | 0.6933 | 0.2785 | Skärholmen | 0.4129 | M0 | Neighbourhood | 0.8384 | 2457 | 0.7228 | XGBoost |
| Stockholm | 38 | 0.6686 | 0.2864 | Skärholmen | 0.4292 | ME | Neighbourhood | 0.8292 | 2457 | 0.7286 | XGBoost |
| Stockholm | 38 | 0.6800 | 0.2868 | Skärholmen | 0.4217 | MW | Neighbourhood | 0.8351 | 2457 | 0.7170 | XGBoost |
| Stockholm | 38 | 0.6788 | 0.2945 | Skärholmen | 0.4226 | MEW | Neighbourhood | 0.8382 | 2457 | 0.7315 | XGBoost |
| Stockholm | 695 | 0.3844 | 0.3290 | Södermalm | 0.4270 | M0 | Neighbourhood | 0.6945 | 1800 | 0.6694 | OLS |
| Stockholm | 695 | 0.4796 | 0.3004 | Södermalm | 0.3926 | ME | Neighbourhood | 0.7047 | 1800 | 0.6811 | OLS |
| Stockholm | 695 | 0.4829 | 0.2991 | Södermalm | 0.3914 | MW | Neighbourhood | 0.7028 | 1800 | 0.6775 | OLS |
| Stockholm | 695 | 0.4861 | 0.2985 | Södermalm | 0.3902 | MEW | Neighbourhood | 0.7040 | 1800 | 0.6787 | OLS |
| Stockholm | 695 | 0.4901 | 0.3030 | Södermalm | 0.3887 | M0 | Neighbourhood | 0.7515 | 1800 | 0.7270 | XGBoost |
| Stockholm | 695 | 0.5594 | 0.2793 | Södermalm | 0.3613 | ME | Neighbourhood | 0.7544 | 1800 | 0.7345 | XGBoost |
| Stockholm | 695 | 0.5616 | 0.2771 | Södermalm | 0.3604 | MW | Neighbourhood | 0.7541 | 1800 | 0.7339 | XGBoost |
| Stockholm | 695 | 0.5621 | 0.2775 | Södermalm | 0.3602 | MEW | Neighbourhood | 0.7527 | 1800 | 0.7336 | XGBoost |
