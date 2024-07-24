cd craft_pytorch
PYTHONPATH=. TORCH_HOME=$(pwd)/craft_pytorch python3 test.py --trained_model=craft_mlt_25k.pth \
                                                              --refiner_model=craft_refiner_CTW1500.pth \
                                                              --test_folder="../input_tmp" \
                                                              --bbox_folder="../output_tmp" \
                                                              --cuda True