import re
import struct
from collections import namedtuple
import math

Header = namedtuple("Header", ["initial_shape", "forests", "forest_size",
                               "tree_depth", "features"])


def read_header(src):
    assert re.search("# version: 1", src.readline()) is not None

    init_match = re.match(r"# initial_shape: (\d+)x(\d+)", src.readline())
    assert init_match is not None

    nrows, ncols = map(int, init_match.groups())

    forests_match = re.match(r"# forests: (\d+)x(\d+)d(\d+)", src.readline())
    assert forests_match is not None

    forest_count, forest_size, tree_depth = map(int, forests_match.groups())

    features_match = re.match(r"# features: (\d+)", src.readline())
    assert features_match is not None
    features = int(features_match.group(1))

    return Header(
        initial_shape=(nrows, ncols),
        forests=forest_count,
        forest_size=forest_size,
        tree_depth=tree_depth,
        features=features,
    )


def convert(src, dst):
    header = read_header(src)
    size = header.initial_shape[0] * header.initial_shape[1]
    print(header, size)

    dst.write(struct.pack(">b6I",
                          1,
                          header.initial_shape[0],
                          header.initial_shape[1],
                          header.forests,
                          header.forest_size,
                          header.tree_depth,
                          header.features))

    initial_shape = list(map(float, src.readline().strip().split(',')))
    assert len(initial_shape) == size

    shape_pack = struct.Struct(f">{size}f")
    node_pack = struct.Struct(">IIh")
    anchor_pack = struct.Struct(f">{header.features}I")
    delta_pack = struct.Struct(">2f")

    dst.write(shape_pack.pack(*initial_shape))

    leafs_count = 2 ** header.tree_depth
    splits_count = leafs_count - 1

    for _ in range(header.forests):
        for _ in range(header.forest_size):
            for _ in range(splits_count):
                idx1, idx2, threshold = src.readline().strip().split(',')
                threshold = int(math.ceil(float(threshold)))
                dst.write(node_pack.pack(int(idx1), int(idx2), threshold))

            for _ in range(leafs_count):
                leaf_values = list(map(float, src.readline().strip().split(',')))
                assert len(leaf_values) == size, "%d != %d" % (len(leaf_values), size)
                dst.write(shape_pack.pack(*leaf_values))

        anchors = list(map(int, src.readline().strip().split(',')))
        assert len(anchors) == header.features
        dst.write(anchor_pack.pack(*anchors))

        for _ in range(header.features):
            x, y = map(float, src.readline().strip().split(','))
            dst.write(delta_pack.pack(x, y))


def main():
    import sys
    from pathlib import Path

    if len(sys.argv) != 3:
        raise Exception("must specify in and out path")

    _, input_path, output_path, *_ = sys.argv
    input_path = Path(input_path).expanduser().absolute()
    output_path = Path(output_path).expanduser().absolute()

    print("convert")
    print("> input: %s" % input_path)
    print("< output: %s" % output_path)

    with input_path.open("r") as file_in:
        with output_path.open("wb") as file_out:
            convert(file_in, file_out)


if __name__ == "__main__":
    main()
