package ch.uzh.beast.evolution.branchratemodel;

import beast.base.core.Description;
import beast.base.core.Input;
import beast.base.inference.parameter.RealParameter;
import beast.base.core.Log;
import beast.base.evolution.branchratemodel.BranchRateModel;
import beast.base.evolution.branchratemodel.StrictClockModel;
import beast.base.evolution.tree.Node;

@Description("Clock model with a constant contribution from each split in the tree, on top of the specified ´branchonlyClock´ branch rate model")
public class BurstClock extends BranchRateModel.Base {

	public Input<RealParameter> persplitInput = new Input<>("perSplit",
			"Effective number of changes after each split in the tree", Input.Validate.REQUIRED);

	public Input<BranchRateModel.Base> branchonlyClockInput = new Input<>("branchonlyClock",
			"The clock model defining the rate along different branches (ignoring splits).", Input.Validate.XOR,
			meanRateInput);

	public Input<RealParameter> birthrateInput = new Input<RealParameter>("birthrate",
			"Birth rate (not effective diversification rate) of the tree, used to infer additional changes after unobserved splits. (Not necessary, but likely makes for better mixing and interpretability.)",
			new RealParameter(new Double[] { 0. }));

	BranchRateModel.Base branchonlyClock;

	@Override
	public void initAndValidate() {
		branchonlyClock = branchonlyClockInput.get();
		if (branchonlyClock == null) {
			// If no branchonly clock is specified, use a is a strict clock.
			branchonlyClock = new StrictClockModel();
			branchonlyClock.initByName("clock.rate", meanRateInput.get());
		} else if (meanRateInput.get() != null) {
			 Log.err.println("WARNING: Explicit branchonly clock was specified for BurstClock " + getID()
			 		+ " so mean rate input will be ignored.");
		}
	}

	@Override
	public double getRateForBranch(final Node node) {
		double perSplit = persplitInput.get().getValue();
		double birthRate = birthrateInput.get().getValue();
		double branchonlyRate = branchonlyClock.getRateForBranch(node);
		double blength = node.getLength();

		if (blength == 0) {
			return branchonlyRate;
		} else {
			double thisIsSplit = 1.0;
			for (Node child : node.getChildren()) {
				if (child.isDirectAncestor()) {
					thisIsSplit = 0.0;
				}
			}
			double splits = thisIsSplit + blength * birthRate;
			return Math.max(branchonlyRate, (splits * perSplit + blength * branchonlyRate) / blength);
		}
	}

	@Override
	public boolean requiresRecalculation() {
		return true;
	}

	@Override
	protected void restore() {
		super.restore();
	}

	@Override
	protected void store() {
		super.store();
	}
}
