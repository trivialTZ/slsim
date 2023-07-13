from lenstronomy.SimulationAPI.sim_api import SimAPI
from astropy.visualization import make_lupton_rgb


def simulate_image(lens_class, band, num_pix, add_noise=True, observatory='LSST', **kwargs):
    """

    :param lens_class: class object containing all information of the lensing system (e.g., GGLens())
    :param band: imaging band
    :param num_pix: number of pixels per axis
    :param add_noise: if True, add noise
    :param observatory: telescope type to be simulated
    :type observatory: str
    :param kwargs: additional keyword arguments for the bands
    :type kwargs: dict
    :return: simulated image
    :rtype: 2d numpy array
    """
    kwargs_model, kwargs_params = lens_class.lenstronomy_kwargs(band)
    from sim_pipeline.Observations import image_quality_lenstronomy
    kwargs_single_band = image_quality_lenstronomy.kwargs_single_band(observatory=observatory, band=band, **kwargs)

    sim_api = SimAPI(numpix=num_pix, kwargs_single_band=kwargs_single_band, kwargs_model=kwargs_model)
    kwargs_lens_light, kwargs_source, kwargs_ps = sim_api.magnitude2amplitude(
        kwargs_lens_light_mag=kwargs_params.get('kwargs_lens_light', None),
        kwargs_source_mag=kwargs_params.get('kwargs_source', None),
        kwargs_ps_mag=kwargs_params.get('kwargs_ps', None))
    kwargs_numerics = {'point_source_supersampling_factor': 1, 'supersampling_factor': 3}
    image_model = sim_api.image_model_class(kwargs_numerics)
    kwargs_lens = kwargs_params.get('kwargs_lens', None)
    image = image_model.image(kwargs_lens=kwargs_lens, kwargs_source=kwargs_source, kwargs_lens_light=kwargs_lens_light,
                              kwargs_ps=kwargs_ps)
    if add_noise:
        image += sim_api.noise_for_model(model=image)
    return image


def sharp_image(lens_class, band, mag_zero_point, delta_pix, num_pix, with_deflector=True):
    """

    :param lens_class: GGLens() object
    :param band: imaging band
    :param mag_zero_point: magnitude zero point in band
    :param delta_pix: pixel scale of image generated
    :param num_pix: number of pixels per axis
    :param with_deflector: bool, if True includes deflector light
    :return: 2d array unblurred image
    """
    kwargs_model, kwargs_params = lens_class.lenstronomy_kwargs(band)
    kwargs_band = {'pixel_scale': delta_pix, 'magnitude_zero_point': mag_zero_point,
                   'background_noise': 0,  # these are keywords not being used but need to be set in SimAPI
                   'psf_type': 'NONE',  # these are keywords not being used but need to be set in SimAPI
                   'exposure_time': 1}  # these are keywords not being used but need to be set in SimAPI
    sim_api = SimAPI(numpix=num_pix, kwargs_single_band=kwargs_band, kwargs_model=kwargs_model)
    kwargs_lens_light, kwargs_source, kwargs_ps = sim_api.magnitude2amplitude(
        kwargs_lens_light_mag=kwargs_params.get('kwargs_lens_light', None),
        kwargs_source_mag=kwargs_params.get('kwargs_source', None),
        kwargs_ps_mag=kwargs_params.get('kwargs_ps', None))
    kwargs_numerics = {'supersampling_factor': 1}
    image_model = sim_api.image_model_class(kwargs_numerics)
    kwargs_lens = kwargs_params.get('kwargs_lens', None)
    image = image_model.image(kwargs_lens=kwargs_lens, kwargs_source=kwargs_source, kwargs_lens_light=kwargs_lens_light,
                              kwargs_ps=kwargs_ps, unconvolved=True, source_add=True, lens_light_add=with_deflector,
                              point_source_add=False)
    return image

def sharp_rgb_image(lens_class, rgb_band_list, mag_zero_point, delta_pix, num_pix):
        """
        Method to generate a sharp rgb-image with lupton_rgb color scale

        :param lens_class: class object containing all information of the lensing system (e.g., GGLens())
        :param rgb_band_list: list of imaging band names corresponding to r-g-b color map
        :param add_noise: boolean flag, set to True to add noise to the image, default is True
        """
        image_r = sharp_image(lens_class=lens_class, band=rgb_band_list[0], mag_zero_point, delta_pix, num_pix)
        image_g = sharp_image(lens_class=lens_class, band=rgb_band_list[1], mag_zero_point, delta_pix, num_pix)
        image_b = sharp_image(lens_class=lens_class, band=rgb_band_list[2], mag_zero_point, delta_pix, num_pix)
        image_rgb = make_lupton_rgb(image_r, image_g, image_b, stretch=0.5)
        return image_rgb