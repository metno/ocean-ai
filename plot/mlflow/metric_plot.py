import glob
import os
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


TOP_METRIC_ALIASES = {
	"train_mse_loss_step": [
		"train_mse_loss_step",
		"train_multi_dataset_loss_step",
		"train/multi_dataset_loss_step",
		"train/mse_loss_step",
		"train_loss_step",
		"train/loss_step",
		"train_mse_step",
	],
	"train_mse_loss_epoch": [
		"train_mse_loss_epoch",
		"train_multi_dataset_loss_epoch",
		"train/multi_dataset_loss_epoch",
		"train/mse_loss_epoch",
		"train_loss_epoch",
		"train/loss_epoch",
		"train_mse_epoch",
	],
	"val_mse_loss_step": [
		"val_mse_loss_step",
		"val_multi_dataset_loss_step",
		"val/multi_dataset_loss_step",
		"val/mse_loss_step",
		"validation_mse_loss_step",
		"validation/loss_step",
		"val_loss_step",
	],
	"val_mse_loss_epoch": [
		"val_mse_loss_epoch",
		"val_multi_dataset_loss_epoch",
		"val/multi_dataset_loss_epoch",
		"val/mse_loss_epoch",
		"validation_mse_loss_epoch",
		"validation/loss_epoch",
		"val_loss_epoch",
	],
	"lr-AdamW": [
		"lr-AdamW",
		"lr_AdamW",
		"lr",
		"learning_rate",
		"optimizer_lr",
	],
	"epoch": [
		"epoch",
		"trainer/epoch",
		"current_epoch",
	],
}

VAL_METRIC_ALIASES = {
	"all": ["all", "overall", "total", "global"],
	"sfc_salinity": ["sfc_salinity", "salinity", "so", "surface_salinity"],
	"sfc_u_eastward": ["sfc_u_eastward", "u_eastward", "uo", "surface_u"],
	"sfc_v_northward": ["sfc_v_northward", "v_northward", "vo", "surface_v"],
	"sfc_temperature": ["sfc_temperature", "temperature", "thetao", "surface_temperature"],
	"sfc_zeta": ["sfc_zeta", "zeta", "zos", "ssh", "surface_height"],
}


def _normalize(name):
	return "".join(c.lower() if c.isalnum() else "" for c in name)


def get_mlflow_dirs(infile, exp_base_dir="/lustre/storeB/project/fou/hi/foccus/experiments/"):
	"""
	Get all matching mlflow metrics dirs from experiment list.
	Input CSV columns: experiment, run_ID, plot_title.
	"""
	df = pd.read_csv(infile, comment="#")

	mlflow_dirs = []
	titles = []
	for i in df.index:
		exp_name = df["experiment"][i]
		run_id_in = df["run_ID"][i]
		title = df["plot_title"][i]

		if title == "*" or title == "":
			title = exp_name
		if run_id_in == "":
			run_id_in = "*"

		run_dir_glob = exp_base_dir + f"{exp_name}/logs/mlflow/*/{run_id_in}/*"
		exp_dirs = [d for d in glob.glob(run_dir_glob) if os.path.isdir(d) and "metrics" in d]
		run_ids = [d.split("/")[-2] for d in exp_dirs]

		if len(exp_dirs) > 1:
			sub_titles = [f"{title} ({rid[:5]})" for rid in run_ids]
		else:
			sub_titles = [title]

		titles.extend(sub_titles)
		mlflow_dirs.extend(exp_dirs)

	print(
		f"Found {len(mlflow_dirs)} relevant mlflow dirs.\n"
		"! Note that some dirs may be empty or incomplete if no metrics were logged."
	)
	return mlflow_dirs, titles


def get_mlflow_metadata(run_dir):
	"""Return run_id and run_name from mlflow run meta.yaml."""
	meta_file = os.path.join(run_dir, "meta.yaml")
	run_id = "unknown"
	run_name = "unknown"
	try:
		with open(meta_file, "r") as f:
			metadata = f.read()
			if "run_id:" in metadata:
				run_id = metadata.split("run_id:")[1].split("\n")[0].strip()
			if "run_name:" in metadata:
				run_name = metadata.split("run_name:")[1].split("\n")[0].strip()
	except Exception as e:
		print(f"Could not read metadata from {meta_file}: {e}")
	return run_id, run_name


def get_config_param(run_dir, param_name):
	"""Return a single MLflow param value from run params directory."""
	config_file = os.path.join(run_dir, "params", param_name)
	try:
		with open(config_file, "r") as f:
			return f.read().strip()
	except Exception:
		return None


def mlflow_multiple_dirs(dir_list, exp_names, suptitle="", figname=""):
	"""Plot canonical metrics from multiple mlflow metrics dirs."""
	if len(dir_list) != len(exp_names):
		print("Error: dir_list and exp_names must have same length!")
		return

	metrics_list = [
		"train_mse_loss_step",
		"train_mse_loss_epoch",
		"val_mse_loss_step",
		"val_mse_loss_epoch",
		"lr-AdamW",
		"epoch",
	]
	val_metrics_list = [
		"all",
		"sfc_salinity",
		"sfc_u_eastward",
		"sfc_v_northward",
		"sfc_temperature",
		"sfc_zeta",
	]

	def _base_title(label):
		return label.split(" (", 1)[0].strip()

	def _sort_segments(segments):
		return sorted(
			segments,
			key=lambda df: float(df["Step"].iloc[0]) if len(df["Step"]) > 0 else float("inf"),
		)

	group_order = []
	group_raw_label = {}
	group_run_count = defaultdict(int)

	top_data = {m: defaultdict(list) for m in metrics_list}
	val_data = {m: defaultdict(list) for m in val_metrics_list}

	fig1, ax1 = plt.subplots(3, 2, figsize=(15, 15))
	fig1.subplots_adjust(wspace=0.12, hspace=0.2, left=0.05, right=0.99, top=0.94, bottom=0.05)
	ax1 = ax1.ravel()
	fig1.suptitle(f"{suptitle}\nMetrics", fontweight="bold", fontsize=15)

	fig2, ax2 = plt.subplots(3, 2, figsize=(15, 12))
	fig2.subplots_adjust(wspace=0.12, hspace=0.2, left=0.05, right=0.99, top=0.94, bottom=0.05)
	ax2 = ax2.ravel()
	fig2.suptitle(
		f"{suptitle}\nValidation metrics: val_mse_inside_lam_metric",
		fontweight="bold",
		fontsize=15,
	)

	for dir_in, experiment in zip(dir_list, exp_names):
		print(f"Processing experiment name: {experiment} in directory: {dir_in}")

		group_key = _base_title(experiment)
		group_raw_label[group_key] = _base_title(experiment)

		if group_key not in group_order:
			group_order.append(group_key)
		group_run_count[group_key] += 1

		for i, metric in enumerate(metrics_list):
			file_path = os.path.join(dir_in, metric)
			if not os.path.isfile(file_path):
				continue

			try:
				ds = pd.read_csv(file_path, sep="\\s+", names=["ID", "Vals", "Step"])
			except Exception as e:
				print(f"Could not read {metric} using Pandas: {e}")
				continue

			if len(ds["Step"]) == 0:
				print(f"Skipping {metric} as it has 0 steps logged.")
				continue

			top_data[metric][group_key].append(ds[["Step", "Vals"]])

		vmetrics_dir = os.path.join(dir_in, "val_mse_inside_lam_metric")
		if not os.path.isdir(vmetrics_dir):
			print(
				f"  No val_mse_inside_lam_metric for {experiment} in directory {dir_in},\n"
				"  --> skipping variable metrics plotting."
			)
			continue

		for j, vmetric in enumerate(val_metrics_list):
			metric_dir = os.path.join(vmetrics_dir, vmetric)
			file_path = os.path.join(metric_dir, "1_scale_0")
			if not os.path.isfile(file_path):
				continue

			try:
				ds_vars = pd.read_csv(file_path, sep="\\s+", names=["ID", "Vals", "Step"])
			except Exception as e:
				print(f"Could not read {file_path} using Pandas: {e}")
				continue

			if len(ds_vars["Step"]) == 0:
				continue

			val_data[vmetric][group_key].append(ds_vars[["Step", "Vals"]])

	palette = list(plt.get_cmap("tab20").colors)
	if not palette:
		palette = ["b", "g", "r", "c", "m", "y", "k"]

	group_colors = {}
	for idx, group_key in enumerate(group_order):
		group_colors[group_key] = palette[idx % len(palette)]

	group_display_label = {}
	for group_key in group_order:
		runs = group_run_count[group_key]
		if runs > 1:
			group_display_label[group_key] = f"{group_raw_label[group_key]} (merged {runs} runs)"
		else:
			group_display_label[group_key] = group_raw_label[group_key]

	for i, metric in enumerate(metrics_list):
		for group_key in group_order:
			segments = top_data[metric].get(group_key, [])
			if not segments:
				continue

			segments = _sort_segments(segments)
			connect_segments = len(segments) > 1
			prev_end = None
			for sidx, seg in enumerate(segments):
				x = seg["Step"]
				y = seg["Vals"]
				ax1[i].plot(
					x,
					y,
					label=group_display_label[group_key] if sidx == 0 else None,
					color=group_colors[group_key],
					linestyle="-",
				)
				if "epoch" in metric:
					ax1[i].scatter(x, y, marker="x", s=3, color=group_colors[group_key])

				if connect_segments and prev_end is not None:
					ax1[i].plot(
						[prev_end[0], x.iloc[0]],
						[prev_end[1], y.iloc[0]],
						color=group_colors[group_key],
						linewidth=1.2,
					)
					ax1[i].scatter([x.iloc[0]], [y.iloc[0]], color="red", s=20, zorder=6)

				prev_end = (x.iloc[-1], y.iloc[-1])

		if "loss" in metric:
			ax1[i].set_yscale("log")

	for j, vmetric in enumerate(val_metrics_list):
		for group_key in group_order:
			segments = val_data[vmetric].get(group_key, [])
			if not segments:
				continue

			segments = _sort_segments(segments)
			connect_segments = len(segments) > 1
			prev_end = None
			for sidx, seg in enumerate(segments):
				x = seg["Step"]
				y = seg["Vals"]
				ax2[j].plot(
					x,
					y,
					label=group_display_label[group_key] if sidx == 0 else None,
					color=group_colors[group_key],
					linestyle="-",
				)
				ax2[j].scatter(x, y, s=4, color="black")

				if connect_segments and prev_end is not None:
					ax2[j].plot(
						[prev_end[0], x.iloc[0]],
						[prev_end[1], y.iloc[0]],
						color=group_colors[group_key],
						linewidth=1.2,
					)
					ax2[j].scatter([x.iloc[0]], [y.iloc[0]], color="red", s=20, zorder=6)

				prev_end = (x.iloc[-1], y.iloc[-1])

	for i, metric in enumerate(metrics_list):
		ax1[i].set_title(metric, fontweight="bold", fontsize=10)
		ax1[i].set_xlabel("Step")
		ax1[i].grid(True, alpha=0.5)
		if ax1[i].lines:
			ax1[i].legend()
		ax2[i].set_yscale("log")

	for j, vmetric in enumerate(val_metrics_list):
		ax2[j].set_title(vmetric, fontweight="bold", fontsize=10)
		ax2[j].set_xlabel("Step")
		ax2[j].grid(True, alpha=0.5)
		if ax2[j].lines:
			ax2[j].legend()

	if figname != "":
		print(f"Saving figures as {figname}_metrics.png and {figname}_val_metrics.png")
		fig1.savefig(figname + "_metrics.png", dpi=200)
		fig2.savefig(figname + "_val_metrics.png", dpi=200)
	else:
		plt.show()


def _collect_metric_files(metrics_dir):
	files = []
	for root, _, fnames in os.walk(metrics_dir):
		for fname in fnames:
			full = Path(root) / fname
			rel = full.relative_to(metrics_dir).as_posix()
			files.append(rel)
	return files


def _resolve_top_metric(metrics_dir, aliases):
	rel_files = _collect_metric_files(metrics_dir)
	by_rel = {p: p for p in rel_files}
	by_norm_rel = {_normalize(p): p for p in rel_files}
	by_norm_base = {_normalize(Path(p).name): p for p in rel_files}

	for alias in aliases:
		if alias in by_rel:
			return metrics_dir / by_rel[alias]

	for alias in aliases:
		key = _normalize(alias)
		if key in by_norm_rel:
			return metrics_dir / by_norm_rel[key]
		if key in by_norm_base:
			return metrics_dir / by_norm_base[key]
	return None


def _collect_val_scale_files(metrics_dir):
	scale_files = []
	for root, _, fnames in os.walk(metrics_dir):
		for fname in fnames:
			if fname != "1_scale_0":
				continue
			full = Path(root) / fname
			parent = full.parent.name
			scale_files.append((parent, full))
	return scale_files


def _resolve_val_metric(metrics_dir, aliases):
	scale_files = _collect_val_scale_files(metrics_dir)
	if not scale_files:
		return None

	by_parent = {parent: full for parent, full in scale_files}
	by_norm_parent = {_normalize(parent): full for parent, full in scale_files}

	for alias in aliases:
		if alias in by_parent:
			return by_parent[alias]

	for alias in aliases:
		key = _normalize(alias)
		if key in by_norm_parent:
			return by_norm_parent[key]
	return None


def _prepare_compatible_metrics_dir(src_metrics_dir, tmp_root):
	src_metrics_dir = Path(src_metrics_dir)
	dst_metrics_dir = Path(tmp_root) / src_metrics_dir.name
	dst_metrics_dir.mkdir(parents=True, exist_ok=True)

	for canonical, aliases in TOP_METRIC_ALIASES.items():
		src = _resolve_top_metric(src_metrics_dir, aliases)
		if src is None:
			continue
		shutil.copy2(src, dst_metrics_dir / canonical)

	val_root = dst_metrics_dir / "val_mse_inside_lam_metric"
	for canonical, aliases in VAL_METRIC_ALIASES.items():
		src = _resolve_val_metric(src_metrics_dir, aliases)
		if src is None:
			continue
		out_dir = val_root / canonical
		out_dir.mkdir(parents=True, exist_ok=True)
		shutil.copy2(src, out_dir / "1_scale_0")

	return str(dst_metrics_dir)


def _build_title(metrics_dir, fallback_title):
	run_dir = str(Path(metrics_dir).parent)
	run_id, run_name = get_mlflow_metadata(run_dir)
	lr = get_config_param(run_dir, "config.training.lr.rate")
	max_steps = get_config_param(run_dir, "config.training.max_steps")

	extras = []
	if lr is not None:
		try:
			extras.append(f"lr={float(lr):.3e}")
		except ValueError:
			pass
	if max_steps is not None:
		try:
			extras.append(f"max_steps={int(max_steps)/1000:g}k")
		except ValueError:
			pass

	base = run_name if run_name != "unknown" else fallback_title
	if run_id != "unknown":
		base = f"{base} ({run_id[:5]})"
	if extras:
		return f"{base}, " + ", ".join(extras)
	return base


def main():
	infile = "experiment_list.csv"
	if not os.path.isfile(infile):
		infile = "../mlflow/experiment_list.csv"
	mlflow_dirs, titles = get_mlflow_dirs(infile)

	temp_roots = []
	compat_dirs = []
	compat_titles = []

	try:
		for metrics_dir, fallback_title in zip(mlflow_dirs, titles):
			tmp_root = tempfile.mkdtemp(prefix="mlflow_metric_plot_", dir=os.environ.get("TMPDIR"))
			temp_roots.append(tmp_root)

			compat_dir = _prepare_compatible_metrics_dir(metrics_dir, tmp_root)
			# Skip runs where no compatible top-level metrics were found.
			if not any((Path(compat_dir) / m).is_file() for m in TOP_METRIC_ALIASES):
				print(f"Skipping {fallback_title}: no recognized metric files in {metrics_dir}")
				continue

			compat_dirs.append(compat_dir)
			compat_titles.append(_build_title(metrics_dir, fallback_title))

		print(f"Plotting {len(compat_dirs)} mlflow directories.")
		if not compat_dirs:
			print("No compatible metrics found to plot.")
			return
		base_figname = "mlflow_learning_rate"
		mlflow_multiple_dirs(compat_dirs, compat_titles, suptitle="many dirs", figname=base_figname)
	finally:
		for tmp_root in temp_roots:
			shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
	main()
