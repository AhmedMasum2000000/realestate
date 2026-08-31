<?php
/**
 * One listing card. Expects $post to be set up by the caller's loop.
 *
 * @var WP_Post $post
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$ref      = get_post_meta( get_the_ID(), 'casa_reference', true );
$price    = get_post_meta( get_the_ID(), 'casa_price', true );
$rent     = get_post_meta( get_the_ID(), 'casa_rent_price', true );
$beds     = get_post_meta( get_the_ID(), 'casa_bedrooms', true );
$baths    = get_post_meta( get_the_ID(), 'casa_bathrooms', true );
$size     = get_post_meta( get_the_ID(), 'casa_size_sqm', true );
$currency = get_post_meta( get_the_ID(), 'casa_currency', true ) ?: 'THB';

$locations = get_the_terms( get_the_ID(), 'listing_location' );
$location  = ( $locations && ! is_wp_error( $locations ) ) ? $locations[0] : null;
?>
<article class="casa-card">
	<a class="casa-card__media" href="<?php the_permalink(); ?>" tabindex="-1" aria-hidden="true">
		<?php if ( has_post_thumbnail() ) : ?>
			<?php the_post_thumbnail( 'medium_large', array( 'loading' => 'lazy', 'alt' => '' ) ); ?>
		<?php else : ?>
			<span class="casa-card__placeholder" aria-hidden="true"></span>
		<?php endif; ?>
		<?php if ( $rent && ! $price ) : ?>
			<span class="casa-card__tag casa-card__tag--rent"><?php esc_html_e( 'For rent', 'casa' ); ?></span>
		<?php elseif ( $price ) : ?>
			<span class="casa-card__tag"><?php esc_html_e( 'For sale', 'casa' ); ?></span>
		<?php endif; ?>
	</a>

	<div class="casa-card__body">
		<?php if ( $location ) : ?>
			<a class="casa-card__place" href="<?php echo esc_url( get_term_link( $location ) ); ?>">
				<?php echo esc_html( $location->name ); ?>
			</a>
		<?php endif; ?>

		<h3 class="casa-card__title">
			<a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
		</h3>

		<p class="casa-card__price">
			<?php echo esc_html( casa_format_price( $price, $rent, $currency ) ); ?>
		</p>

		<ul class="casa-card__facts">
			<?php if ( $beds ) : ?>
				<li><strong><?php echo esc_html( (string) (int) $beds ); ?></strong> <?php esc_html_e( 'bed', 'casa' ); ?></li>
			<?php endif; ?>
			<?php if ( $baths ) : ?>
				<li><strong><?php echo esc_html( rtrim( rtrim( (string) $baths, '0' ), '.' ) ); ?></strong> <?php esc_html_e( 'bath', 'casa' ); ?></li>
			<?php endif; ?>
			<?php if ( $size ) : ?>
				<li><strong><?php echo esc_html( rtrim( rtrim( (string) $size, '0' ), '.' ) ); ?></strong> <?php esc_html_e( 'sqm', 'casa' ); ?></li>
			<?php endif; ?>
		</ul>

		<?php if ( $ref ) : ?>
			<p class="casa-card__ref"><?php echo esc_html( $ref ); ?></p>
		<?php endif; ?>
	</div>
</article>
