import argparse
import matplotlib.pyplot as plt

from census_tract_cleaning import DATA_DIR, load_tracts


def main(show_plot=False):
    tracts = load_tracts()

    ax = tracts.plot(
        figsize=(10, 10),
        facecolor='none',
        edgecolor='black',
        linewidth=0.2,
    )
    ax.set_title('Census Tract Boundaries (EPSG:4269 source CRS)')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    output_path = DATA_DIR / 'tract_boundaries_preview.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')

    print(f'Preview saved to: {output_path}')
    if show_plot:
        plt.show()
    else:
        plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot census tract boundaries.')
    parser.add_argument(
        '--show',
        action='store_true',
        help='Display an interactive plot window after saving the image.',
    )
    args = parser.parse_args()
    main(show_plot=args.show)
