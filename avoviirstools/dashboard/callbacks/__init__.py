def init_callbacks(flusher):
    from .data_arrival import DataArrival

    data_arrival = DataArrival()
    flusher.flushables.append(data_arrival)

    from .product_generation import ProductGeneration

    product_generation = ProductGeneration()
    flusher.flushables.append(product_generation)

    from .volcview_images import VolcviewImages

    volcview_images = VolcviewImages()
    flusher.flushables.append(volcview_images)
